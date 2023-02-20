from flask import Flask, render_template, redirect,request
import firebase_admin
from firebase_admin import credentials, firestore,auth



cred = credentials.Certificate("capstone.json")
firebase_admin.initialize_app(cred)
store = firestore.client()

app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def landing():
    return render_template("landing.html")


@app.route('/signup/<string:type>',methods = ['GET','POST'])
def signup(type):
    userid=""
    message=""
    details = {}
    skills = []

    if request.method == 'POST':
        useremail=request.form["email"]
        userpassword=request.form["password"]
        mobile=request.form["mobile"]
        if type == "recruiter":
            company=request.form["company"]
            jobtitle=request.form["jobtitle"]
            cinfo = request.form["companyinfo"]
            jobinfo = request.form["jinfo"]
        elif type == "seeker":
            skills = request.form["skills"].split(',')
        try:
            print("inside")
            user=auth.create_user(
            email=useremail,
            email_verified=False,
            password=userpassword)
            message="Succesfully created user"
            userid = user.uid
            dit = {}
            dit["email"] = useremail
            dit['password'] = userpassword
            dit['mobile'] = mobile
            if type == "recruiter":
                dit['company'] = company
                dit['jobtitle'] = jobtitle
                dit["companyinfo"] = cinfo
                dit["jobinfo"] = jobinfo
            elif type == "seeker":
                dit["skills"] = skills

            else:
                dit["email"] = useremail
                dit["password"] = userpassword
                dit["phone"] = request.form["mobile"]
            
            store.collection(type).add(dit)

            url = '/jobs/'+type+"/"+useremail
            return redirect(url)
        except:
            message="User already exists"

        print(message)
        details["comp"] = company
    
    details["type"] = type

    #return jsonify("uid:",uid,"message:",message)
    return render_template("authenticate.html",person = details)



@app.route('/login/<string:type>',methods = ['GET','POST'])
def login(type):
    dit = {}
    message = ""
    details = {}
    print(f"method is {request.method}")
    if request.method == 'POST':
        
        useremail=request.form["email"]
        details["email"] = useremail
        userpassword=request.form["password"]
        message=""
        uid=""
        try:
            user=auth.get_user_by_email(useremail)
            message="Woohooo, succesfully logged in"
            uid=user.uid
            docs = store.collection(type).stream()
            for doc in docs:
                if doc.to_dict().get("email") == useremail:
                    emailid = useremail
                    break
    
            url = '/jobs/'+type+"/"+useremail
            return redirect(url)
        except:
            message="User authentication failed"

    
    details["type"] = type

    return render_template("login.html",detail = details)

@app.route('/jobs/<string:type>/<string:eid>',methods = ['GET','POST'])
def viewjobs(type,eid):
    joblst = []
    info = {}
    idlst = []
    if type == "recruiter":
        docs = store.collection("recruiter").stream()
        for doc in docs:
            dit = {}
            if doc.to_dict().get("email") == eid:
                dit = doc.to_dict()
                dit["id"] = doc.id
                joblst.append(dit)
    elif type == "seeker" or type == "admin":
        docs = store.collection("recruiter").stream()
        for doc in docs:
            dit = {}
            dit = doc.to_dict()
            dit["id"] = doc.id
            joblst.append(dit)

    info["type"] = type
    info["jobs"] = joblst
    info["eid"] = eid

    return render_template("jobs.html",data = info)


@app.route('/addjob/<string:type>/<string:eid>',methods = ['GET','POST'])
def addjobs(type,eid):
    details = {}
    details["type"] = type
    details["email"] = eid
    docs = store.collection("recruiter").stream()
    for doc in docs:
        if doc.to_dict().get("email") == eid:
            details["company"] = doc.to_dict().get("company")
            details["companyinfo"] = doc.to_dict().get("companyinfo")
    if request.method == "POST":
        company = request.form["company"]
        title = request.form["title"]
        info = request.form["info"]
        jinfo = request.form["jinfo"]
        dit = {}
        dit["company"] = company
        dit["jobtitle"] = title
        dit["companyinfo"] = info
        dit["jobinfo"] = jinfo
        dit["email"] = eid
        store.collection(type).add(dit)
        url = "/jobs/"+type+"/"+eid
        return redirect(url)
    return render_template("addjob.html",detail = details)

@app.route('/viewdetails/<string:eid>/<string:id>/<string:type>',methods = ['GET','POST'])
def viewdetails(eid,id,type):
    dit = {}
    dit["type"] = type
    docs = store.collection("recruiter").stream()
    for doc in docs:
        if doc.id == id:
            dit["email"] = eid
            dit["id"] = id
            dit["job"] = doc.to_dict()
            break
    return render_template("details.html",job = dit)

@app.route('/register/<string:eid>/<string:id>/<string:type>',methods = ['GET'])
def register(eid,id,type):

    docs = store.collection("recruiter").stream()
    for doc in docs:
        if doc.id == id:
            dit = doc.to_dict()
            dit["useremail"] = eid

    store.collection("applications").add(dit)

    return redirect("/myapplication/"+eid+"/"+type)




@app.route('/myapplication/<string:eid>/<string:type>',methods = ['GET','POST'])
def myapp(eid,type):
    lst = []
    dit = {}
    dit["type"] = type
    dit["email"] = eid
    docs = store.collection("applications").stream()
    if type == "admin":
        for doc in docs:
            lst.append(doc.to_dict())

    else:
        for doc in docs:
            if doc.to_dict().get("useremail") == eid:
                lst.append(doc.to_dict())
    
    dit["applied"] = lst


    return render_template("myapp.html",apps = dit)

@app.route('/deletejob/<string:id>/<string:type>/<string:eid>',methods = ['GET','POST'])
def deletejob(id,type,eid):
    store.collection("recruiter").document(id).delete()
    return redirect("/jobs/"+type+"/"+eid)


@app.route('/updatejob/<string:id>/<string:type>/<string:eid>',methods = ['GET','POST'])
def updatejob(id,type,eid):
    dit = {}
    
    docs = store.collection("recruiter").stream()
    for doc in docs:
        if doc.id == id:
            dit = doc.to_dict()
            break

    dit["id"] = id
    dit["eid"] = eid
    dit["type"] = type

    if request.method == 'POST':
        send = {}
        company= request.form["comp"]
        jobtitle= request.form["title"]
        companyinfo= request.form["info"]
        jobinfo = request.form["jinfo"]
        email = request.form["compemail"]

        send["company"] = company
        send["jobtitle"] = jobtitle
        send["companyinfo"] = companyinfo
        send["jobinfo"] = jobinfo
        send["email"] = email

        store.collection("recruiter").document(id).update(send)

        return redirect("/jobs/"+type+"/"+eid)
    
    return render_template("updatejob.html",updatedetail = dit)
    

    

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port = "3000",debug=True)


