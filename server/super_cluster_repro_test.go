package server

import (
	"fmt"
	"net"
	"strings"
	"testing"
)

// TestJetStreamSuperClusterLocalhostMetaLeader exercises a JetStream
// meta-leader election failure that appears when a super-cluster is configured
// with a route/gateway hostname that resolves to more than one IP (e.g.
// "localhost" on a dual-stack host).
//
// bootstrapRaftNode estimates the meta-Raft size by adding len(net.LookupHost(host))
// per gateway URL (see server/raft.go bootstrapRaftNode). With "localhost"
// → [127.0.0.1, ::1] each gateway URL contributes 2 instead of 1, inflating
// the expected cluster size and preventing quorum. With "127.0.0.1" the
// IP-literal branch runs and the count is correct.
func TestJetStreamSuperClusterLocalhostMetaLeader(t *testing.T) {
	if addrs, _ := net.LookupHost("localhost"); len(addrs) < 2 {
		t.Skip(`requires "localhost" to resolve to multiple IPs (dual-stack)`)
	}

	// Rewrite only the route/gateway URLs (scheme nats-route://) to use
	// "localhost"; leave the various listen: 127.0.0.1:N lines alone.
	toLocalhost := func(_, _, _, conf string) string {
		conf = strings.ReplaceAll(conf, "nats-route://127.0.0.1:", "nats-route://localhost:")
		fmt.Println(conf)
		return conf
	}

	sc := createJetStreamSuperClusterWithTemplateAndModHook(t, jsClusterTempl, 3, 2, toLocalhost, nil)
	defer sc.shutdown()
}
