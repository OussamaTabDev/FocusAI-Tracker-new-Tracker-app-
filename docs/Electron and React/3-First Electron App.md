✅ **Great! Let’s continue our journey — we’re now at:**

---

# 🟣 **Chapter 3: Creating Your First Electron App (with features)**

---

## 🌟 In this chapter:

👉 We’ll go beyond “Hello, Electron!”
👉 We’ll add:

* A custom window size
* A title
* A custom icon (optional)
* A menu (basic)
* A button that triggers an action

---

## 🛠 **Step-by-Step Example**

### 1️⃣ **Project setup (if not done yet):**

```bash
mkdir my-electron-app
cd my-electron-app
npm init -y
npm install electron --save-dev
```

---

### 2️⃣ **File structure**

```
my-electron-app/
 ├── main.js
 ├── index.html
 └── package.json
```

---

### 3️⃣ **main.js**

```javascript
const { app, BrowserWindow, Menu } = require('electron')
const path = require('path')

function createWindow () {
  const win = new BrowserWindow({
    width: 1024,
    height: 768,
    title: 'My First Electron App',
    icon: path.join(__dirname, 'icon.png'), // optional icon
    webPreferences: {
      nodeIntegration: true
    }
  })

  win.loadFile('index.html')

  // Build a basic menu
  const template = [
    {
      label: 'File',
      submenu: [
        { role: 'quit' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'toggledevtools' }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
```

---

### 4️⃣ **index.html**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>My First Electron App</title>
</head>
<body>
  <h1>Welcome to Electron!</h1>
  <button id="btn">Click Me!</button>

  <script>
    document.getElementById('btn').addEventListener('click', () => {
      alert('You clicked the button!');
    });
  </script>
</body>
</html>
```

---

### 5️⃣ **package.json script**

```json
"scripts": {
  "start": "electron ."
}
```

---

### 6️⃣ **Run the app**

```bash
npm start
```

✅ You should see:

* A window with 1024×768 size
* A title “My First Electron App”
* A simple menu: File (Quit), View (Reload, Toggle DevTools)
* A button that shows an alert

---

## 🌟 Chapter 3 Summary

✔ You created a basic Electron app
✔ You added window configs, a menu, and interactivity
✔ You’re ready for deeper concepts (main/renderer separation, better UI)

---

👉 **Say “next chapter” to continue to Chapter 4: Main & Renderer Process in Action.**
Or: ask for “add multi-window example” / “add tray icon” / “custom styles”.
