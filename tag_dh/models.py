from tag_dh import db

class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    health = db.Column(db.Integer, nullable=False)

    members = db.relationship("Account")


class Submission(db.Model):
    __tablename__ = 'submission'

    id = db.Column(db.Integer, primary_key=True)
    percent_mark = db.Column(db.Integer)  # null = unmarked
    # percent_mark = db.Column(db.Integer, nullable=False)
    
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    task = db.relationship("Task", back_populates="submissions")

    def __repr__(self):
        return f'<Submission: id={self.id!r} percent_mark={self.percent_mark!r}>'


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=True)

    submissions = db.relationship("Submission", back_populates="task")

    def __repr__(self):
        return f'<Task: {self.name}>'


# Links between Post, Clash, and Account

'''   unused
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
'''

class Post(db.Model):
    __tablename__ = "post"
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Post: id={self.id!r}>'

class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Text, nullable=False)
    pwrd = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)
    badges = db.Column(db.Text, nullable=True)
    
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)  # can be None (teamless)
    team = db.relationship("Team", back_populates="members")

    def __repr__(self):
        return f'<Account: id={self.id!r} user={self.user!r}>'

'''
class Clash(db.Model):
    __tablename__ = 'clash'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    posts = db.relationship("PostClashLink", back_populates="clash")
    accounts = db.relationship("ClashAccountLink", back_populates="clash")

    def __repr__(self):
        return f'<Clash: id={self.id!r} name={self.name!r}>'
'''
