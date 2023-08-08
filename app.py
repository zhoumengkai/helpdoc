from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
db = SQLAlchemy(app)

# 创建数据库模型
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=True)
    children = db.relationship('Document', backref=db.backref('parent', remote_side=[id]))

# 建立应用上下文并创建数据库表
with app.app_context():
    db.create_all()

# 定义主页路由
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        parent_id = int(request.form['parent_id']) if request.form['parent_id'] else None

        document = Document(title=title, content=content, parent_id=parent_id)
        db.session.add(document)
        db.session.commit()

        flash('Document added successfully!', 'success')
        return redirect(url_for('index'))

    documents = Document.query.filter_by(parent_id=None).all()
    return render_template('index.html', documents=documents)
# 定义编辑文档路由
@app.route('/edit/<int:document_id>', methods=['GET', 'POST'])
def edit_document(document_id):
    document = Document.query.get_or_404(document_id)

    if request.method == 'POST':
        document.title = request.form['title']
        document.content = request.form['content']
        db.session.commit()

        flash('Document updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_document.html', document=document)

# 定义删除文档路由
@app.route('/delete/<int:document_id>', methods=['POST'])
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    # 递归删除文档及其所有子文档
    def recursive_delete(doc):
        for child in doc.children:
            recursive_delete(child)
            db.session.delete(child)
        db.session.delete(doc)

    recursive_delete(document)
    db.session.commit()

    flash('Document deleted successfully!', 'success')
    return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug=True)
