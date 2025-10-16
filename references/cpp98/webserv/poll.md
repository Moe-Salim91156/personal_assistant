=== LANGUAGE: poll() (CPP98 / Webserv) ===

WHAT IS POLL()?
poll() is a **system call for monitoring multiple file descriptors** to see if I/O is possible.  
- More scalable than select() for many clients.  
- Monitors sockets (or other fds) for: readable, writable, or error conditions.  
- Used in Webserv to handle **multiple clients simultaneously** without blocking.  

KEY CONCEPTS:
- struct pollfd: describes each fd to monitor
    - fd: file descriptor
    - events: events to watch (POLLIN, POLLOUT, POLLERR, POLLHUP, POLLNVAL)
    - revents: events that occurred
- timeout: wait time in milliseconds (-1 = infinite, 0 = poll and return immediately)
- Returns number of fds ready, 0 if timeout, -1 on error

---

HEADERS / IMPORTS:
#include <poll.h>
#include <unistd.h>
#include <fcntl.h>
#include <cerrno>
#include <iostream>
#include <vector>
#include <cstring>

---

DECLARATION / SYNTAX:
int poll(struct pollfd *fds, nfds_t nfds, int timeout);

---

PARAMETERS / DETAILS:

pollfd struct:
- fd: file descriptor to monitor
- events: bitmask of requested events
    - POLLIN = data to read
    - POLLOUT = ready to write
    - POLLERR = error condition
    - POLLHUP = hang up
    - POLLNVAL = invalid fd
- revents: bitmask set by kernel with occurred events

poll():
- fds: array of pollfd structs
- nfds: number of fds in the array
- timeout: milliseconds to wait (-1 = infinite)
- Returns: number of fds with events, 0 on timeout, -1 on error

recv()/send() (common with poll):
- buf: buffer pointer
- len: buffer length
- flags: usually 0
- Returns: bytes read/written, 0 on disconnect, -1 on error

---

BASIC EXAMPLE:
std::vector<pollfd> fds;
pollfd server_fd;
server_fd.fd = sockfd;
server_fd.events = POLLIN;
fds.push_back(server_fd);

int ready = poll(fds.data(), fds.size(), 1000); // 1 second timeout
if (ready > 0) {
    for (size_t i = 0; i < fds.size(); i++) {
        if (fds[i].revents & POLLIN) {
            char buffer[1024];
            int bytes = recv(fds[i].fd, buffer, sizeof(buffer), 0);
            if (bytes <= 0) {
                // client disconnected or error
                close(fds[i].fd);
                fds.erase(fds.begin() + i);
                i--;
            } else {
                std::cout << "Received: " << std::string(buffer, bytes) << std::endl;
            }
        }
    }
}

---

ADVANCED CONSIDERATIONS:
- Combine poll() with non-blocking sockets for scalable servers
- Check revents for POLLERR, POLLHUP, POLLNVAL to handle errors
- Dynamic vector of pollfd allows adding/removing clients at runtime
- Always update nfds / vector after removing disconnected clients
- Works with TCP, UDP, pipes, terminals

---

GOTCHAS:
- Forgetting to check revents → may miss errors or hangups
- Using blocking sockets → poll may indicate ready but recv() still blocks
- Modifying pollfd array while iterating → iterate carefully
- Timeout = 0 → busy loop; timeout = -1 → blocks indefinitely

---

42 SPECIFIC NOTES:
- Use poll() to manage multiple clients instead of select() for large number
- Must handle disconnects gracefully (recv() = 0)
- Keep functions <25 lines (norm compliance)
- Manual parsing after recv() for HTTP requests

---

CPP98 CONSTRAINTS:
- No range-based for; use explicit loops
- No auto keyword
- Use std::vector or arrays for pollfd storage
- Manual memory management if needed

---

RELATED CONCEPTS:
- select()
- recv()/send()
- Non-blocking sockets
- Sockets, HTTP parsing, Webserv concurrency

