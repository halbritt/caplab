// Command beacond polls the fastest regional status endpoint on an
// interval and prints a rolling availability summary.
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"beacond/internal/config"
	"beacond/internal/probe"
	"beacond/internal/report"
)

func main() {
	var (
		endpointsFlag = flag.String("endpoints", "", "comma-separated status endpoint URLs")
		interval      = flag.Duration("interval", 10*time.Second, "time between polls")
		timeout       = flag.Duration("timeout", 5*time.Second, "per-request HTTP timeout")
		window        = flag.Int("window", 360, "polls kept for the rolling summary")
	)
	flag.Parse()

	endpoints, err := config.Endpoints(*endpointsFlag)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		flag.Usage()
		os.Exit(2)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	prober := probe.New(*timeout)
	tracker := report.NewTracker(*window)

	log.Printf("beacond: polling %d endpoints every %s", len(endpoints), interval)
	ticker := time.NewTicker(*interval)
	defer ticker.Stop()

	for {
		res, err := prober.Fastest(ctx, endpoints)
		if err != nil {
			log.Printf("poll failed: %v", err)
			tracker.Record(report.Sample{When: time.Now()})
		} else {
			tracker.Record(report.Sample{
				Endpoint: res.Endpoint,
				Healthy:  res.Status.Healthy,
				Elapsed:  res.Elapsed,
				When:     time.Now(),
			})
			log.Printf("%s answered in %s (healthy=%t) | %s",
				res.Endpoint, res.Elapsed.Round(time.Millisecond), res.Status.Healthy,
				tracker.Snapshot().Line())
		}

		select {
		case <-ctx.Done():
			log.Print("beacond: shutting down")
			return
		case <-ticker.C:
		}
	}
}
