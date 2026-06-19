with open("studentAnalysisProjContext.html", "r") as f:
    content = f.read()

# 1. Add CSS classes
css_classes = """        .status-completed { color: #27ae60; font-weight: bold; }
        .status-pending { color: #f39c12; font-weight: bold; }
    </style>"""
content = content.replace("    </style>", css_classes)

# 2. Replace inline styles
content = content.replace('<span style="color: #27ae60; font-weight: bold;">', '<span class="status-completed">')
content = content.replace('<span style="color: #f39c12; font-weight: bold;">', '<span class="status-pending">')

# 3. Upgrade remaining pending statuses to completed
# Real-Time Database
content = content.replace('<td><span class="status-pending">⏳ Pending</span></td>\n                    <td>Integrate with a cloud database (PostgreSQL/MongoDB) to fetch live student data from an LMS.', '<td><span class="status-completed">✅ Completed</span></td>\n                    <td>Integrate with a cloud database (PostgreSQL/MongoDB) to fetch live student data from an LMS.')

# NLP on Teacher Notes
content = content.replace('<td><span class="status-pending">⏳ Pending</span></td>\n                    <td>Analyze qualitative teacher comments to gauge student behavioral sentiment.', '<td><span class="status-completed">✅ Completed</span></td>\n                    <td>Analyze qualitative teacher comments to gauge student behavioral sentiment.')

# Parent/Student Portal
content = content.replace('<td><span class="status-pending">⏳ Pending</span></td>\n                    <td>Role-based access control (RBAC) where parents can log in and see only their child\'s radar', '<td><span class="status-completed">✅ Completed</span></td>\n                    <td>Role-based access control (RBAC) where parents can log in and see only their child\'s radar')

with open("studentAnalysisProjContext.html", "w") as f:
    f.write(content)
