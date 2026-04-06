# iPhone Prototyping Guide

This guide shows how to test Emmaus on a real iPhone 11 during local development.

## What you need

- your development machine running Emmaus
- your iPhone 11
- both devices on the same Wi-Fi network

## 1. Start Emmaus so your phone can reach it

Run Emmaus with the server bound to your local network interface instead of only localhost.

```bash
uvicorn emmaus.main:app --host 0.0.0.0 --port 8000 --reload
```

`0.0.0.0` makes the dev server reachable from other devices on your network.

## 2. Find your computer's local IP address

On Windows, run:

```bash
ipconfig
```

Look for your Wi-Fi adapter's IPv4 address.

It will look something like:

```text
192.168.1.42
```

## 3. Open Emmaus on your iPhone 11

On the iPhone, open Safari and go to:

```text
http://YOUR-IP-ADDRESS:8000
```

Example:

```text
http://192.168.1.42:8000
```

If everything is set up correctly, Emmaus should load on the phone.

## 4. If it does not load

Common causes:

- the phone and computer are on different Wi-Fi networks
- Windows Firewall is blocking Python or port `8000`
- the server is still bound only to `127.0.0.1`

If Windows asks whether to allow Python or the dev server on your network, allow it for your private network.

## 5. Best way to test on iPhone 11

Use Safari first, because that reflects the real iPhone browser environment.

Focus on these checks:

- first-run onboarding
- Bible selection and ESV connection flow
- session readability on a smaller screen
- sticky navigation behavior
- form spacing and tap targets
- keyboard overlap with textareas and buttons
- source preview cards and nudge cards

## 6. Add Emmaus to the Home Screen

If you want it to feel more app-like:

1. Open Emmaus in Safari.
2. Tap the Share button.
3. Tap **Add to Home Screen**.

This is useful for testing a lightweight app-like experience even before a dedicated mobile wrapper exists.

## 7. Suggested iPhone 11 test loop

A good fast loop is:

1. run Emmaus locally
2. open it on the iPhone 11
3. walk through onboarding
4. start a session
5. complete an action item
6. preview nudges
7. adjust the UI based on what feels cramped or unclear

## 8. Optional next step for remote testing

If you want to test Emmaus away from your home network or share it with someone else, the next step would be a secure dev tunnel such as a staging deployment or a tunneling tool.

For now, the local Wi-Fi setup is the simplest and safest way to prototype on your iPhone 11.
