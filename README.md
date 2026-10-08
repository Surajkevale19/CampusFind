# 🎓 Campus Lost & Found Marketplace (MVP)

A peer-to-peer campus web application where students can report lost or found items, browse a searchable marketplace, and request/claim items by submitting verifiable **Proof of Ownership**.

---

## 🚀 Key Features Built for this MVP

1. **Marketplace & Browse Feed (`/`)**
   - Live search by keyword, item title, or campus location (e.g. *Library*, *AirPods*, *Calculator*).
   - Filter by Type: **All Listings**, **Found Items (Claimable)**, or **Lost Items**.
   - Filter by Category (*Electronics*, *Wallets & IDs*, *Keys*, *Books*, etc.) and Status (*Available*, *Claim Pending*, *Reunited*).
   - Quick Community Statistics: Total items listed, active claims, and items reunited.

2. **Report / Upload Lost & Found Items (`/post`)**
   - Simple, responsive upload form with campus-specific fields (exact location, date, category).
   - Image upload support (local device upload or paste image URL).
   - **Privacy Guidance**: Advises finders not to reveal secret identifying details publicly.
   - **4-Digit Management PIN**: The uploader sets a simple PIN (e.g., `1234`) to review claims and approve the rightful owner without needing heavy login screens for the MVP.

3. **Claim with Proof of Ownership (`/item/<id>`)**
   - Prevents dishonest claims by requiring claimants to submit hidden details (e.g., lock screen wallpaper, specific engravings, inside wallet contents, scratch marks, serial numbers).
   - Allows uploading proof files (invoices, photos with the item, student ID).

4. **Uploader Verification & Handover Station**
   - The original poster enters their PIN to unlock the management portal on the item page.
   - Compares submitted claims side-by-side with submitted proof.
   - **Accept Proof**: Marks the item as **Reunited 🎉** and exchanges contact details.
   - **Decline Proof**: Rejects unverified claims.

5. **Campus Safe Exchange Guidelines (`/guidelines`)**
   - Clear best practices for safe meetups at campus security or library reception.

---

## 🛠️ Tech Stack

- **Backend**: Python 3 (Flask)
- **Database**: SQLite3 (`lost_and_found.db` - automatically created with demo data)
- **Frontend**: HTML5, Tailwind CSS (Modern, mobile-responsive UI), Jinja2 templates
- **File Uploads**: Handled securely via `werkzeug.utils.secure_filename` into `static/uploads/`

---

## 🏃 Quick Start (How to Run)

### Method 1: Using the command line
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Method 2: Double-click launcher
Double-click `run.bat` in this folder.

---

## 🎬 How to Demo This Project (Walkthrough Guide)

1. **Open the Homepage (`http://127.0.0.1:5000`)**:
   - Show the items already pre-loaded into the system (AirPods in Library, Casio Calculator in Physics Lab, Spiderman lanyard keys).
   - Test the search bar: type `AirPods` or `Library`.

2. **Upload a New Item**:
   - Click **"Report an Item"** in the top right.
   - Select *"I Found Something"*, fill out title *"Dell Laptop Charger"*, location *"Room 204"*, and create PIN `1234`.
   - Click *"Publish Listing"*.

3. **Submit a Claim with Proof**:
   - Open any item (e.g. the Casio Calculator or your new item).
   - Scroll to **"Request Item with Proof"**.
   - Fill in your name, email, and explain the proof: *"It has a blue ink mark on the sliding cover and serial ending in 442"*.
   - Click *"Submit Claim with Proof"*.
   - Notice the status updates to **"Proof Review / Claim Pending"**.

4. **Verify Proof as Uploader**:
   - On the same item page, scroll to **"Uploader Portal"**.
   - Enter PIN `1234` and click *"Unlock Claims"*.
   - See the claim you just submitted with its full proof text!
   - Click **"Accept Proof & Mark Reunited"**.
   - Notice the item status changes to **"Reunited / Returned 🎉"**!
