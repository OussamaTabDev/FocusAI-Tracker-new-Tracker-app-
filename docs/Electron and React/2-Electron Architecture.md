✅ **Awesome! Let’s move on to Chapter 2: this will give you a solid understanding of how Electron works behind the scenes.**

---

# 🟣 **Chapter 2: Understanding Electron Architecture**

---

## 🌐 **Electron's Core Idea**

Electron combines:

* **Chromium** → Displays your UI (like a browser window)
* **Node.js** → Gives you backend/server-like powers (file system, OS interaction, etc.)

This means:
👉 You can create apps that **look like a website**
👉 But they can **do things a website can’t** (e.g., read files, control menus)

---

## ⚙️ **Main concepts**

### 🟣 Main Process

* It runs in Node.js.
* It creates and manages windows.
* There is **only one main process**.
* It controls app lifecycle (open, close, minimize).

👉 Example: `main.js` is your main process file.

---

### 🟣 Renderer Process

* Each window has its own renderer process.
* Runs your **web pages** (HTML, CSS, JS).
* Like a tab in Chrome.
* Can use limited Node.js APIs (unless you allow more).

---

### 🟣 BrowserWindow

* Electron class that represents a desktop window.
* Created in the main process.
* Loads your UI (usually an HTML file or a URL).

Example:

```javascript
const win = new BrowserWindow({
  width: 800,
  height: 600
})
win.loadFile('index.html')
```

---

## 🛡 **Why separate processes?**

👉 Security: The renderer runs untrusted web code, main handles privileged OS tasks.
👉 Stability: One renderer crashes → other windows stay alive.
👉 Control: Main process manages global state of your app.

---

## 🔌 **Inter-Process Communication (IPC)**

Because main + renderer are separate:
👉 They **communicate via IPC channels**.

✅ Renderer can **send a message** to main
✅ Main can **reply or send messages** to renderer

(E.g. ask main process to open a file dialog)

We’ll cover IPC deeply in Chapter 9.

---

## 📝 **App Lifecycle Events**

Your main process listens for app events:

```javascript
app.on('ready', createWindow)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
```

* `ready`: Electron is ready to create windows.
* `window-all-closed`: All windows closed (app can quit).
* `activate`: macOS: app reactivated from dock.

---

## 🔍 **Visual of Electron architecture**

```
 ┌────────────┐        IPC        ┌───────────────┐
 │ Main       │ <----------------> │ Renderer      │
 │ (Node.js)  │                    │ (HTML/CSS/JS) │
 └────────────┘                    └───────────────┘
         │
         └── Creates BrowserWindow
```

✅ Main process = Manager
✅ Renderer = UI

---

## 🌟 Chapter 2 Summary

✔ You understand Electron’s architecture: main vs renderer
✔ You know why they’re separated
✔ You’re ready to create multi-window apps + communicate between processes

---

👉 **Say “next chapter” to proceed to Chapter 3: Creating Your First Electron App (with more features)**
👉 Or: “generate diagram” / “deeper explanation on main/renderer” / “code example multi-window” — your choice!
