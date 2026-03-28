package memory

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type Memory struct {
	db *sql.DB
}

type LogEntry struct {
	Input   string
	Intent  string
	Result  string
	Success bool
	At      time.Time
}

func Open(path string) (*Memory, error) {
	// expand ~/
	if strings.HasPrefix(path, "~/") {
		home, _ := os.UserHomeDir()
		path = filepath.Join(home, path[2:])
	}

	os.MkdirAll(filepath.Dir(path), 0755)

	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, err
	}

	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS sessions (
			id        INTEGER PRIMARY KEY AUTOINCREMENT,
			input     TEXT,
			intent    TEXT,
			result    TEXT,
			success   BOOLEAN,
			at        DATETIME DEFAULT CURRENT_TIMESTAMP
		);
		CREATE TABLE IF NOT EXISTS context (
			key       TEXT PRIMARY KEY,
			value     TEXT,
			updated   DATETIME DEFAULT CURRENT_TIMESTAMP
		);
	`)
	if err != nil {
		return nil, err
	}

	return &Memory{db: db}, nil
}

func (m *Memory) Close() {
	m.db.Close()
}

// Log saves every interaction — input, what jarvis did, result
func (m *Memory) Log(input string, result any) {
	type resultShape interface {
		GetIntent() string
		GetOutput() string
		IsSuccess() bool
	}

	// flexible — store whatever we can
	m.db.Exec(
		`INSERT INTO sessions (input, intent, result, success) VALUES (?, ?, ?, ?)`,
		input, fmt.Sprintf("%v", result), "", true,
	)
}

// LastCommand returns the most recent logged command
func (m *Memory) LastCommand() *LogEntry {
	row := m.db.QueryRow(
		`SELECT input, intent, result, success, at 
		 FROM sessions ORDER BY id DESC LIMIT 1`,
	)
	var e LogEntry
	var t string
	if err := row.Scan(&e.Input, &e.Intent, &e.Result, &e.Success, &t); err != nil {
		return nil
	}
	e.At, _ = time.Parse("2006-01-02 15:04:05", t)
	return &e
}

// LastSession returns a human-readable summary of the last session
func (m *Memory) LastSession() string {
	rows, err := m.db.Query(
		`SELECT input, success, at FROM sessions 
		 WHERE date(at) = date('now', '-1 day')
		 ORDER BY id DESC LIMIT 5`,
	)
	if err != nil || rows == nil {
		return ""
	}
	defer rows.Close()

	var parts []string
	for rows.Next() {
		var input string
		var success bool
		var at string
		rows.Scan(&input, &success, &at)
		status := "✓"
		if !success {
			status = "✗"
		}
		parts = append(parts, fmt.Sprintf("%s %s", status, input))
	}

	if len(parts) == 0 {
		return ""
	}
	return strings.Join(parts, ", ")
}

// RecentContext returns last N commands as a string for LLM context
func (m *Memory) RecentContext(n int) string {
	rows, err := m.db.Query(
		`SELECT input, intent FROM sessions ORDER BY id DESC LIMIT ?`, n,
	)
	if err != nil {
		return ""
	}
	defer rows.Close()

	var parts []string
	for rows.Next() {
		var input, intent string
		rows.Scan(&input, &intent)
		parts = append(parts, fmt.Sprintf("- %q → %s", input, intent))
	}
	return strings.Join(parts, "\n")
}

// Set stores a key/value in the context table (e.g. last terraform dir)
func (m *Memory) Set(key, value string) {
	m.db.Exec(
		`INSERT INTO context (key, value, updated) VALUES (?, ?, CURRENT_TIMESTAMP)
		 ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated=CURRENT_TIMESTAMP`,
		key, value,
	)
}

// Get retrieves a context value
func (m *Memory) Get(key string) string {
	var value string
	m.db.QueryRow(`SELECT value FROM context WHERE key = ?`, key).Scan(&value)
	return value
}
