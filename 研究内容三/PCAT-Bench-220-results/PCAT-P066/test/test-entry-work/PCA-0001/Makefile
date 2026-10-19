# Build PCA-0001 reproducer
# Requires: analysis_repo built with ./autogen.sh && make
# Usage: make ANALYSIS_REPO=/path/to/patched/worktree
ANALYSIS_REPO ?= ../../_worktrees/patched
BUILD_DIR ?= $(ANALYSIS_REPO)

CFLAGS = -I$(ANALYSIS_REPO) -I$(ANALYSIS_REPO)/runtime -g -O0
LDFLAGS = -L$(BUILD_DIR)/runtime/.libs -lrsyslog

all: reproducer

reproducer: reproducer.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f reproducer

.PHONY: all clean
