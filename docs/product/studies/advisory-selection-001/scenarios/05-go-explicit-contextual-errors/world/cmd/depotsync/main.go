// Command depotsync mirrors manifest entries from a content archive
// into a destination directory tree.
package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/meridian-ops/depotsync/internal/manifest"
	"github.com/meridian-ops/depotsync/internal/store"
	"github.com/meridian-ops/depotsync/internal/syncer"
)

func main() {
	manifestPath := flag.String("manifest", "depot.json", "manifest file listing entries to mirror")
	archive := flag.String("archive", "", "archive root directory (source)")
	dest := flag.String("dest", "", "destination directory tree")
	flag.Parse()

	if *archive == "" || *dest == "" {
		fmt.Fprintln(os.Stderr, "usage: depotsync -manifest depot.json -archive DIR -dest DIR")
		os.Exit(2)
	}

	m, err := manifest.Load(*manifestPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "depotsync: %v\n", err)
		os.Exit(1)
	}
	st, err := store.New(*archive)
	if err != nil {
		fmt.Fprintf(os.Stderr, "depotsync: %v\n", err)
		os.Exit(1)
	}
	res, err := syncer.New(st, *dest).Run(m)
	if err != nil {
		fmt.Fprintf(os.Stderr, "depotsync: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("sync complete: %d synced, %d skipped\n", res.Synced, res.Skipped)
}
