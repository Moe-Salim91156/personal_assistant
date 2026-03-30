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

func (m *Memory) Log(input string, result any) {
	m.db.Exec(
		`INSERT INTO sessions (input, intent, result, success) VALUES (?, ?, ?, ?)`,
		input, fmt.Sprintf("%v", result), "", true,
	)
}

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
