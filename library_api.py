"""
Library Management System - RESTful API
Built with Flask | In-memory storage (swap with SQLAlchemy for production)
"""

from flask import Flask, jsonify, request, abort
from datetime import datetime, timedelta
import uuid
import re

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ─────────────────────────────────────────
# In-Memory Data Store
# ─────────────────────────────────────────

books = {
    "b001": {
        "id": "b001", "isbn": "978-0-06-112008-4", "title": "To Kill a Mockingbird",
        "author": "Harper Lee", "genre": "Fiction", "year": 1960,
        "copies_total": 5, "copies_available": 3,
        "created_at": "2024-01-10T08:00:00Z", "updated_at": "2024-01-10T08:00:00Z"
    },
    "b002": {
        "id": "b002", "isbn": "978-0-7432-7356-5", "title": "1984",
        "author": "George Orwell", "genre": "Dystopian Fiction", "year": 1949,
        "copies_total": 4, "copies_available": 2,
        "created_at": "2024-01-11T09:00:00Z", "updated_at": "2024-01-11T09:00:00Z"
    },
    "b003": {
        "id": "b003", "isbn": "978-0-14-028329-7", "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald", "genre": "Fiction", "year": 1925,
        "copies_total": 3, "copies_available": 3,
        "created_at": "2024-01-12T10:00:00Z", "updated_at": "2024-01-12T10:00:00Z"
    },
}

members = {
    "m001": {
        "id": "m001", "name": "Alice Johnson", "email": "alice@example.com",
        "phone": "+1-555-0101", "membership_type": "premium",
        "active_loans": 1, "max_loans": 10,
        "joined_at": "2024-01-05T00:00:00Z", "updated_at": "2024-01-05T00:00:00Z"
    },
    "m002": {
        "id": "m002", "name": "Bob Smith", "email": "bob@example.com",
        "phone": "+1-555-0102", "membership_type": "standard",
        "active_loans": 2, "max_loans": 5,
        "joined_at": "2024-01-06T00:00:00Z", "updated_at": "2024-01-06T00:00:00Z"
    },
}

loans = {
    "l001": {
        "id": "l001", "book_id": "b001", "member_id": "m001",
        "loaned_at": "2024-01-15T10:00:00Z",
        "due_at": "2024-02-15T10:00:00Z",
        "returned_at": None, "status": "active",
        "created_at": "2024-01-15T10:00:00Z"
    },
    "l002": {
        "id": "l002", "book_id": "b002", "member_id": "m002",
        "loaned_at": "2024-01-20T11:00:00Z",
        "due_at": "2024-02-20T11:00:00Z",
        "returned_at": None, "status": "active",
        "created_at": "2024-01-20T11:00:00Z"
    },
}

# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def new_id(prefix):
    return prefix + str(uuid.uuid4())[:8]

def paginate(data_list, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return data_list[start:end]

def success(data, status=200, meta=None):
    body = {"success": True, "data": data}
    if meta:
        body["meta"] = meta
    return jsonify(body), status

def error(message, status=400, code=None):
    body = {"success": False, "error": {"message": message}}
    if code:
        body["error"]["code"] = code
    return jsonify(body), status

def validate_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)

# ─────────────────────────────────────────
# Root & Health
# ─────────────────────────────────────────

@app.route('/')
def root():
    return jsonify({
        "name": "Library Management API",
        "version": "1.0.0",
        "description": "RESTful API for library book and member management",
        "docs": "/api/v1/docs",
        "endpoints": {
            "books":   "/api/v1/books",
            "members": "/api/v1/members",
            "loans":   "/api/v1/loans",
            "search":  "/api/v1/search?q=query",
            "stats":   "/api/v1/stats",
            "health":  "/api/v1/health",
        }
    })

@app.route('/api/v1/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": now_iso(),
        "counts": {
            "books": len(books),
            "members": len(members),
            "loans": len(loans),
            "active_loans": sum(1 for l in loans.values() if l["status"] == "active")
        }
    })

# ─────────────────────────────────────────
# BOOKS — CRUD
# ─────────────────────────────────────────

@app.route('/api/v1/books', methods=['GET'])
def get_books():
    page     = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 50)
    genre    = request.args.get('genre')
    author   = request.args.get('author')
    available = request.args.get('available')

    result = list(books.values())

    if genre:
        result = [b for b in result if genre.lower() in b['genre'].lower()]
    if author:
        result = [b for b in result if author.lower() in b['author'].lower()]
    if available == 'true':
        result = [b for b in result if b['copies_available'] > 0]

    total = len(result)
    paged = paginate(result, page, per_page)

    return success(paged, meta={
        "page": page, "per_page": per_page,
        "total": total, "pages": -(-total // per_page)
    })


@app.route('/api/v1/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = books.get(book_id)
    if not book:
        return error(f"Book '{book_id}' not found", 404, "BOOK_NOT_FOUND")
    return success(book)


@app.route('/api/v1/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data:
        return error("Request body must be JSON", 400, "INVALID_BODY")

    required = ['title', 'author', 'isbn']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400, "MISSING_FIELDS")

    # Check duplicate ISBN
    if any(b['isbn'] == data['isbn'] for b in books.values()):
        return error(f"A book with ISBN '{data['isbn']}' already exists", 409, "DUPLICATE_ISBN")

    book_id = new_id("b")
    copies  = max(int(data.get('copies_total', 1)), 1)
    book = {
        "id":               book_id,
        "isbn":             data['isbn'],
        "title":            data['title'],
        "author":           data['author'],
        "genre":            data.get('genre', 'Uncategorized'),
        "year":             data.get('year'),
        "copies_total":     copies,
        "copies_available": copies,
        "created_at":       now_iso(),
        "updated_at":       now_iso(),
    }
    books[book_id] = book
    return success(book, 201)


@app.route('/api/v1/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    book = books.get(book_id)
    if not book:
        return error(f"Book '{book_id}' not found", 404, "BOOK_NOT_FOUND")

    data = request.get_json()
    if not data:
        return error("Request body must be JSON", 400, "INVALID_BODY")

    updatable = ['title', 'author', 'genre', 'year', 'copies_total']
    for field in updatable:
        if field in data:
            book[field] = data[field]

    # Recalculate available if total changed
    if 'copies_total' in data:
        loaned_out = book['copies_total'] - book['copies_available']
        book['copies_available'] = max(book['copies_total'] - loaned_out, 0)

    book['updated_at'] = now_iso()
    return success(book)


@app.route('/api/v1/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = books.get(book_id)
    if not book:
        return error(f"Book '{book_id}' not found", 404, "BOOK_NOT_FOUND")

    # Prevent deletion if active loans exist
    active = [l for l in loans.values() if l['book_id'] == book_id and l['status'] == 'active']
    if active:
        return error("Cannot delete book with active loans. Return all copies first.", 409, "BOOK_ON_LOAN")

    del books[book_id]
    return success({"id": book_id, "deleted": True})

# ─────────────────────────────────────────
# MEMBERS — CRUD
# ─────────────────────────────────────────

@app.route('/api/v1/members', methods=['GET'])
def get_members():
    page     = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 50)
    mtype    = request.args.get('membership_type')

    result = list(members.values())
    if mtype:
        result = [m for m in result if m['membership_type'] == mtype]

    total = len(result)
    return success(paginate(result, page, per_page), meta={
        "page": page, "per_page": per_page,
        "total": total, "pages": -(-total // per_page)
    })


@app.route('/api/v1/members/<member_id>', methods=['GET'])
def get_member(member_id):
    member = members.get(member_id)
    if not member:
        return error(f"Member '{member_id}' not found", 404, "MEMBER_NOT_FOUND")
    return success(member)


@app.route('/api/v1/members', methods=['POST'])
def create_member():
    data = request.get_json()
    if not data:
        return error("Request body must be JSON", 400, "INVALID_BODY")

    required = ['name', 'email']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400, "MISSING_FIELDS")

    if not validate_email(data['email']):
        return error("Invalid email address format", 400, "INVALID_EMAIL")

    if any(m['email'] == data['email'] for m in members.values()):
        return error(f"A member with email '{data['email']}' already exists", 409, "DUPLICATE_EMAIL")

    mtype   = data.get('membership_type', 'standard')
    max_lns = 10 if mtype == 'premium' else 5

    member_id = new_id("m")
    member = {
        "id":               member_id,
        "name":             data['name'],
        "email":            data['email'],
        "phone":            data.get('phone', ''),
        "membership_type":  mtype,
        "active_loans":     0,
        "max_loans":        max_lns,
        "joined_at":        now_iso(),
        "updated_at":       now_iso(),
    }
    members[member_id] = member
    return success(member, 201)


@app.route('/api/v1/members/<member_id>', methods=['PUT'])
def update_member(member_id):
    member = members.get(member_id)
    if not member:
        return error(f"Member '{member_id}' not found", 404, "MEMBER_NOT_FOUND")

    data = request.get_json()
    if not data:
        return error("Request body must be JSON", 400, "INVALID_BODY")

    if 'email' in data:
        if not validate_email(data['email']):
            return error("Invalid email address format", 400, "INVALID_EMAIL")
        if any(m['email'] == data['email'] and m['id'] != member_id for m in members.values()):
            return error("Email already used by another member", 409, "DUPLICATE_EMAIL")

    for field in ['name', 'email', 'phone', 'membership_type']:
        if field in data:
            member[field] = data[field]

    if 'membership_type' in data:
        member['max_loans'] = 10 if data['membership_type'] == 'premium' else 5

    member['updated_at'] = now_iso()
    return success(member)


@app.route('/api/v1/members/<member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = members.get(member_id)
    if not member:
        return error(f"Member '{member_id}' not found", 404, "MEMBER_NOT_FOUND")

    if member['active_loans'] > 0:
        return error("Cannot delete member with active loans. Return all books first.", 409, "MEMBER_HAS_LOANS")

    del members[member_id]
    return success({"id": member_id, "deleted": True})

# ─────────────────────────────────────────
# LOANS — CRUD + Return
# ─────────────────────────────────────────

@app.route('/api/v1/loans', methods=['GET'])
def get_loans():
    page     = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 50)
    status   = request.args.get('status')
    member   = request.args.get('member_id')
    book     = request.args.get('book_id')

    result = list(loans.values())
    if status:
        result = [l for l in result if l['status'] == status]
    if member:
        result = [l for l in result if l['member_id'] == member]
    if book:
        result = [l for l in result if l['book_id'] == book]

    total = len(result)
    return success(paginate(result, page, per_page), meta={
        "page": page, "per_page": per_page,
        "total": total, "pages": -(-total // per_page)
    })


@app.route('/api/v1/loans/<loan_id>', methods=['GET'])
def get_loan(loan_id):
    loan = loans.get(loan_id)
    if not loan:
        return error(f"Loan '{loan_id}' not found", 404, "LOAN_NOT_FOUND")
    return success(loan)


@app.route('/api/v1/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    if not data:
        return error("Request body must be JSON", 400, "INVALID_BODY")

    required = ['book_id', 'member_id']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400, "MISSING_FIELDS")

    book   = books.get(data['book_id'])
    member = members.get(data['member_id'])

    if not book:
        return error(f"Book '{data['book_id']}' not found", 404, "BOOK_NOT_FOUND")
    if not member:
        return error(f"Member '{data['member_id']}' not found", 404, "MEMBER_NOT_FOUND")
    if book['copies_available'] < 1:
        return error("No copies available for this book", 409, "NO_COPIES_AVAILABLE")
    if member['active_loans'] >= member['max_loans']:
        return error(f"Member has reached their loan limit ({member['max_loans']})", 409, "LOAN_LIMIT_REACHED")

    loan_days = int(data.get('loan_days', 30))
    due = (datetime.utcnow() + timedelta(days=loan_days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    loan_id = new_id("l")
    loan = {
        "id":          loan_id,
        "book_id":     data['book_id'],
        "member_id":   data['member_id'],
        "loaned_at":   now_iso(),
        "due_at":      due,
        "returned_at": None,
        "status":      "active",
        "created_at":  now_iso(),
    }
    loans[loan_id] = loan
    book['copies_available'] -= 1
    member['active_loans']   += 1

    return success(loan, 201)


@app.route('/api/v1/loans/<loan_id>/return', methods=['PATCH'])
def return_book(loan_id):
    loan = loans.get(loan_id)
    if not loan:
        return error(f"Loan '{loan_id}' not found", 404, "LOAN_NOT_FOUND")
    if loan['status'] == 'returned':
        return error("This book has already been returned", 409, "ALREADY_RETURNED")

    loan['returned_at'] = now_iso()
    loan['status']      = 'returned'

    book   = books.get(loan['book_id'])
    member = members.get(loan['member_id'])
    if book:
        book['copies_available'] = min(book['copies_available'] + 1, book['copies_total'])
    if member:
        member['active_loans'] = max(member['active_loans'] - 1, 0)

    return success(loan)


@app.route('/api/v1/loans/<loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    loan = loans.get(loan_id)
    if not loan:
        return error(f"Loan '{loan_id}' not found", 404, "LOAN_NOT_FOUND")
    if loan['status'] == 'active':
        return error("Cannot delete an active loan. Return the book first.", 409, "LOAN_ACTIVE")
    del loans[loan_id]
    return success({"id": loan_id, "deleted": True})

# ─────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────

@app.route('/api/v1/search', methods=['GET'])
def search():
    q = request.args.get('q', '').lower().strip()
    if not q or len(q) < 2:
        return error("Query 'q' must be at least 2 characters", 400, "QUERY_TOO_SHORT")

    matched_books = [
        b for b in books.values()
        if q in b['title'].lower() or q in b['author'].lower()
           or q in b['genre'].lower() or q in b['isbn']
    ]
    matched_members = [
        m for m in members.values()
        if q in m['name'].lower() or q in m['email'].lower()
    ]

    return success({
        "query": q,
        "books":   matched_books,
        "members": matched_members,
        "counts":  {"books": len(matched_books), "members": len(matched_members)}
    })

# ─────────────────────────────────────────
# STATS
# ─────────────────────────────────────────

@app.route('/api/v1/stats', methods=['GET'])
def stats():
    active_loans   = [l for l in loans.values() if l['status'] == 'active']
    returned_loans = [l for l in loans.values() if l['status'] == 'returned']
    overdue        = [l for l in active_loans if l['due_at'] < now_iso()]

    genre_counts = {}
    for b in books.values():
        genre_counts[b['genre']] = genre_counts.get(b['genre'], 0) + 1

    return success({
        "books": {
            "total":            len(books),
            "total_copies":     sum(b['copies_total'] for b in books.values()),
            "available_copies": sum(b['copies_available'] for b in books.values()),
            "genres":           genre_counts,
        },
        "members": {
            "total":    len(members),
            "premium":  sum(1 for m in members.values() if m['membership_type'] == 'premium'),
            "standard": sum(1 for m in members.values() if m['membership_type'] == 'standard'),
        },
        "loans": {
            "total":    len(loans),
            "active":   len(active_loans),
            "returned": len(returned_loans),
            "overdue":  len(overdue),
        }
    })

# ─────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return error("Endpoint not found", 404, "NOT_FOUND")

@app.errorhandler(405)
def method_not_allowed(e):
    return error("Method not allowed on this endpoint", 405, "METHOD_NOT_ALLOWED")

@app.errorhandler(500)
def server_error(e):
    return error("Internal server error", 500, "SERVER_ERROR")

if __name__ == '__main__':
    print("🚀 Library API running at http://localhost:5000")
    app.run(debug=True, port=5000)
