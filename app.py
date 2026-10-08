import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = 'campus_lost_and_found_secret_key_demo_2026'

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

CATEGORIES = [
    "Electronics",
    "Wallets & IDs",
    "Keys",
    "Books & Stationery",
    "Clothing & Accessories",
    "Bags & Backpacks",
    "Personal Items",
    "Others"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    item_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')
    status = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'newest')

    conn = get_db()
    cursor = conn.cursor()

    # Base query
    sql = 'SELECT * FROM items WHERE 1=1'
    params = []

    if query:
        sql += ' AND (title LIKE ? OR description LIKE ? OR location LIKE ?)'
        pattern = f'%{query}%'
        params.extend([pattern, pattern, pattern])

    if item_type in ['found', 'lost']:
        sql += ' AND item_type = ?'
        params.append(item_type)

    if category != 'all' and category in CATEGORIES:
        sql += ' AND category = ?'
        params.append(category)

    if status in ['open', 'claim_pending', 'resolved']:
        sql += ' AND status = ?'
        params.append(status)

    if sort_by == 'oldest':
        sql += ' ORDER BY created_at ASC'
    else:
        sql += ' ORDER BY created_at DESC'

    cursor.execute(sql, params)
    items = cursor.fetchall()

    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM items')
    total_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE item_type = 'found'")
    total_found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE item_type = 'lost'")
    total_lost = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'resolved'")
    total_resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM claims")
    total_claims = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'index.html',
        items=items,
        categories=CATEGORIES,
        query=query,
        item_type=item_type,
        category=category,
        status=status,
        sort_by=sort_by,
        stats={
            'total': total_items,
            'found': total_found,
            'lost': total_lost,
            'resolved': total_resolved,
            'claims': total_claims
        }
    )

@app.route('/post', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        item_type = request.form.get('item_type', 'found')
        category = request.form.get('category', 'Others')
        location = request.form.get('location', '').strip()
        date_occurred = request.form.get('date_occurred', '').strip()
        description = request.form.get('description', '').strip()
        contact_name = request.form.get('contact_name', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        secret_pin = request.form.get('secret_pin', '').strip()

        if not title or not location or not description or not contact_name or not contact_email or not secret_pin:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('post_item'))

        # Handle image upload
        image_url = None
        file = request.files.get('item_image')
        if file and file.filename != '' and allowed_file(file.filename):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"item_{timestamp}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = url_for('static', filename=f'uploads/{filename}')
        else:
            custom_url = request.form.get('image_url', '').strip()
            if custom_url:
                image_url = custom_url

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO items (
                title, item_type, category, location, date_occurred,
                description, image_url, contact_name, contact_email,
                contact_phone, secret_pin, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open')
        ''', (
            title, item_type, category, location, date_occurred,
            description, image_url, contact_name, contact_email,
            contact_phone, secret_pin
        ))
        conn.commit()
        new_item_id = cursor.lastrowid
        conn.close()

        flash(f'Item "{title}" successfully listed on the marketplace! Save your PIN ({secret_pin}) to review claims.', 'success')
        return redirect(url_for('item_detail', item_id=new_item_id))

    return render_template('post_item.html', categories=CATEGORIES)

@app.route('/item/<int:item_id>', methods=['GET'])
def item_detail(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        flash('Item not found.', 'error')
        return redirect(url_for('index'))

    # Check if uploader unlocked this item session
    is_authorized = session.get(f'auth_item_{item_id}', False)

    # Fetch claims if authorized or for status check
    cursor.execute('SELECT * FROM claims WHERE item_id = ? ORDER BY created_at DESC', (item_id,))
    claims = cursor.fetchall()

    conn.close()

    return render_template(
        'item_detail.html',
        item=item,
        claims=claims,
        is_authorized=is_authorized
    )

@app.route('/item/<int:item_id>/claim', methods=['POST'])
def submit_claim(item_id):
    claimant_name = request.form.get('claimant_name', '').strip()
    claimant_email = request.form.get('claimant_email', '').strip()
    claimant_phone = request.form.get('claimant_phone', '').strip()
    claimant_student_id = request.form.get('claimant_student_id', '').strip()
    proof_description = request.form.get('proof_description', '').strip()

    if not claimant_name or not claimant_email or not proof_description:
        flash('Please fill in your name, email, and proof details to file a claim.', 'error')
        return redirect(url_for('item_detail', item_id=item_id))

    proof_image_url = None
    file = request.files.get('proof_file')
    if file and file.filename != '' and allowed_file(file.filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"proof_{timestamp}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        proof_image_url = url_for('static', filename=f'uploads/{filename}')

    conn = get_db()
    cursor = conn.cursor()

    # Insert claim
    cursor.execute('''
        INSERT INTO claims (
            item_id, claimant_name, claimant_email, claimant_phone,
            claimant_student_id, proof_description, proof_image_url, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', (
        item_id, claimant_name, claimant_email, claimant_phone,
        claimant_student_id, proof_description, proof_image_url
    ))

    # Update item status to 'claim_pending' if it was open
    cursor.execute('''
        UPDATE items
        SET status = CASE WHEN status = 'open' THEN 'claim_pending' ELSE status END
        WHERE id = ?
    ''', (item_id,))

    conn.commit()
    conn.close()

    flash('Your claim with proof was successfully submitted! The finder/poster has been notified to review your proof.', 'success')
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/item/<int:item_id>/verify-pin', methods=['POST'])
def verify_pin(item_id):
    pin_input = request.form.get('secret_pin', '').strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT secret_pin FROM items WHERE id = ?', (item_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row['secret_pin'] == pin_input:
        session[f'auth_item_{item_id}'] = True
        flash('PIN verified! You can now manage claims, verify proof, and update item status.', 'success')
    else:
        flash('Incorrect PIN. Please enter the PIN you created when uploading this item.', 'error')

    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/item/<int:item_id>/logout-admin')
def logout_admin(item_id):
    session.pop(f'auth_item_{item_id}', None)
    flash('Logged out of owner management view.', 'info')
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/claim/<int:claim_id>/action', methods=['POST'])
def claim_action(claim_id):
    action = request.form.get('action') # 'approve' or 'reject'
    notes = request.form.get('decision_notes', '').strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM claims WHERE id = ?', (claim_id,))
    claim = cursor.fetchone()

    if not claim:
        conn.close()
        flash('Claim not found.', 'error')
        return redirect(url_for('index'))

    item_id = claim['item_id']

    # Security check: must be authenticated for this item
    if not session.get(f'auth_item_{item_id}', False):
        conn.close()
        flash('Unauthorized. Please enter the item PIN first.', 'error')
        return redirect(url_for('item_detail', item_id=item_id))

    if action == 'approve':
        cursor.execute("UPDATE claims SET status = 'approved', decision_notes = ? WHERE id = ?", (notes, claim_id))
        # Mark other claims as rejected
        cursor.execute("UPDATE claims SET status = 'rejected', decision_notes = 'Another verified claim was approved.' WHERE item_id = ? AND id != ?", (item_id, claim_id))
        # Mark item as resolved/reunited
        cursor.execute("UPDATE items SET status = 'resolved' WHERE id = ?", (item_id,))
        conn.commit()
        flash(f'Claim by {claim["claimant_name"]} approved! Item is now marked as Reunited 🎉 Contact them directly to complete the handover.', 'success')
    elif action == 'reject':
        cursor.execute("UPDATE claims SET status = 'rejected', decision_notes = ? WHERE id = ?", (notes, claim_id))
        # Check if any remaining pending claims exist
        cursor.execute("SELECT COUNT(*) FROM claims WHERE item_id = ? AND status = 'pending'", (item_id,))
        pending_count = cursor.fetchone()[0]
        if pending_count == 0:
            cursor.execute("UPDATE items SET status = 'open' WHERE id = ?", (item_id,))
        conn.commit()
        flash('Claim rejected. Item remains open for other potential claimants.', 'info')

    conn.close()
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/guidelines')
def guidelines():
    return render_template('guidelines.html')

if __name__ == '__main__':
    init_db()
    print("Starting Campus Lost & Found Marketplace on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
