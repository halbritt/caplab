// hashcheck recomputes striatum change-set result_tree_hash values using the
// PRODUCTION arithmetic (internal/changeset) from ~/git/striatum-next,
// imported read-only. Two modes:
//
//	hashcheck -cs <changeset.json> -base <canonical-product-file>
//	    base tree given directly (a dispatch inputs/01-base body).
//
//	hashcheck -cs <changeset.json> -objects <dir>
//	    base tree composed from the change set's own base_composition:
//	    observed product body + ancestor change-set bodies are read from
//	    <dir>/<content_hash> (pre-decompressed), folded with ApplyOverlay in
//	    application_index order, exactly as composePacketBase does.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"github.com/halbritt/striatum-next/internal/changeset"
	"github.com/halbritt/striatum-next/internal/gitanchor"
)

func sha(b []byte) string {
	s := sha256.Sum256(b)
	return hex.EncodeToString(s[:])
}

func die(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "FATAL: "+format+"\n", args...)
	os.Exit(2)
}

func loadObject(dir, hash string) []byte {
	body, err := os.ReadFile(filepath.Join(dir, hash))
	if err != nil {
		die("object %s: %v", hash, err)
	}
	if got := sha(body); got != hash {
		die("object %s decompressed to wrong hash %s", hash, got)
	}
	return body
}

func main() {
	csPath := flag.String("cs", "", "change set JSON path")
	basePath := flag.String("base", "", "canonical product body (materialized base)")
	objects := flag.String("objects", "", "dir of pre-decompressed bodies named by content hash")
	repo := flag.String("repo", "", "git repo root for expanding a git-anchored base (read-only)")
	flag.Parse()

	csBody, err := os.ReadFile(*csPath)
	if err != nil {
		die("%v", err)
	}
	fmt.Printf("change_set_body_sha256      = %s\n", sha(csBody))
	cs, err := changeset.ParseChangeSet(csBody)
	if err != nil {
		die("parse change set: %v", err)
	}
	fmt.Printf("declared_base_hash (pin)    = %s\n", cs.BaseHash())
	fmt.Printf("declared_result_tree_hash   = %s\n", cs.ResultTreeHash)

	var base changeset.Product
	switch {
	case *basePath != "":
		raw, err := os.ReadFile(*basePath)
		if err != nil {
			die("%v", err)
		}
		fmt.Printf("base_file_raw_sha256        = %s\n", sha(raw))
		base, err = changeset.ParseProduct(raw)
		if err != nil {
			die("parse base product: %v", err)
		}
	case *objects != "":
		if cs.BaseComposition == nil {
			die("change set has no base_composition")
		}
		bc := cs.BaseComposition
		obsBody := loadObject(*objects, bc.ObservedProduct.ContentHash)
		base, err = changeset.ParseProduct(obsBody)
		if err != nil {
			die("parse observed product: %v", err)
		}
		anc := append([]changeset.IndexedChangeSetPin(nil), bc.Ancestors...)
		sort.Slice(anc, func(i, j int) bool { return anc[i].ApplicationIndex < anc[j].ApplicationIndex })
		for _, a := range anc {
			ancBody := loadObject(*objects, a.ChangeSet.ContentHash)
			ancCS, err := changeset.ParseChangeSet(ancBody)
			if err != nil {
				die("parse ancestor %d: %v", a.ApplicationIndex, err)
			}
			next, conflicts := changeset.ApplyOverlay(base, ancCS)
			if len(conflicts) > 0 {
				die("ancestor %d overlay conflicts: %+v", a.ApplicationIndex, conflicts)
			}
			base = next
		}
	default:
		die("need -base or -objects")
	}

	baseHash, err := changeset.TreeHash(base)
	if err != nil {
		die("%v", err)
	}
	fmt.Printf("computed_base_tree_hash     = %s\n", baseHash)
	if baseHash == cs.BaseHash() {
		fmt.Println("BASE PIN: MATCHES computed base tree")
	} else {
		fmt.Println("BASE PIN: DOES NOT MATCH computed base tree")
	}

	// Mirror driver.Session.deriveResultTreeHash: the pin comparison is
	// against the small anchored body's hash, but the overlay applies to the
	// EXPANDED tree when the base is git-anchored.
	applied := base
	if base.Anchor != nil {
		if *repo == "" {
			fmt.Println("base is git-anchored; pass -repo to expand (result below is the UNEXPANDED arithmetic)")
		} else {
			expanded, err := gitanchor.Expand(*repo, base)
			if err != nil {
				die("expand anchored base: %v", err)
			}
			expHash, err := changeset.TreeHash(expanded)
			if err != nil {
				die("%v", err)
			}
			fmt.Printf("expanded_base_tree_hash     = %s\n", expHash)
			applied = expanded
		}
	}

	result, conflicts := changeset.ApplyOverlay(applied, cs)
	if len(conflicts) > 0 {
		die("subject overlay conflicts: %+v", conflicts)
	}
	resultHash, err := changeset.TreeHash(result)
	if err != nil {
		die("%v", err)
	}
	fmt.Printf("computed_result_tree_hash   = %s\n", resultHash)
	if resultHash == cs.ResultTreeHash {
		fmt.Println("RESULT: DECLARED HASH REPRODUCES EXACTLY")
	} else {
		fmt.Println("RESULT: DECLARED HASH DOES NOT REPRODUCE")
	}

	// Also run the strict production Apply for completeness.
	if _, cf := changeset.Apply(applied, baseHash, cs); len(cf) > 0 {
		fmt.Printf("strict Apply conflicts: %+v\n", cf)
	} else {
		fmt.Println("strict Apply: clean")
	}
}
