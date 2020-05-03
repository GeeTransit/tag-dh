from tag_dh import db

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Task: {self.name}>'


# Links between Post, Clash, and Account

class PostClashLink(db.Model):
    __tablename__ = 'postclashlink'

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    clash_id = db.Column(db.Integer, db.ForeignKey('clash.id'), primary_key=True)
    relationType = db.Column(db.String(24))
    post = db.relationship("Post", back_populates="clashes")
    clash = db.relationship("Clash", back_populates="posts")

class PostAccountLink(db.Model):
    __tablename__ = 'postaccountlink'

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    relationType = db.Column(db.String(24))
    post = db.relationship("Post", back_populates="accounts")
    account = db.relationship("Account", back_populates="posts")

class ClashAccountLink(db.Model):
    __tablename__ = 'clashaccountlink'

    clash_id = db.Column(db.Integer, db.ForeignKey('clash.id'), primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    relationType = db.Column(db.String(24))
    clash = db.relationship("Clash", back_populates="accounts")
    account = db.relationship("Account", back_populates="clashes")


class Post(db.Model):
    __tablename__ = "post"
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    clashes = db.relationship("PostClashLink", back_populates="post")
    accounts = db.relationship("PostAccountLink", back_populates="post")

    def __repr__(self):
        return f'<Post: id={self.id!r}>'

class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Text, nullable=False)
    pwrd = db.Column(db.Text, nullable=False)

    posts = db.relationship("PostAccountLink", back_populates="account")
    clashes = db.relationship("ClashAccountLink", back_populates="account")

    def __repr__(self):
        return f'<Account: id={self.id!r} user={self.user!r}>'

class Clash(db.Model):
    __tablename__ = 'clash'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    posts = db.relationship("PostClashLink", back_populates="clash")
    accounts = db.relationship("ClashAccountLink", back_populates="clash")

    def __repr__(self):
        return f'<Clash: id={self.id!r} name={self.name!r}>'
