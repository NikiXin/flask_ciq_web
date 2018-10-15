from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import json
import os
import time
from CIQ_parser import *
from CIQ_redis import *
from CIQ_data import *
import requests
import predictionio

app = Flask(__name__)
app.secret_key = "ormuco"
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['xlsx', 'txt'])
my_redis = CiqRedis()
error = None



@app.route('/engine/<username>', methods =['GET','POST'])
def engine(username):
    favoriate_tools = my_redis.get_user_tool(username)
    role_tools = my_redis.get_user_tool('h'+username)

    engine_client = predictionio.EngineClient(url="http://167.99.183.243:8000")
    recommended_tool_properties = []
    favoriate_tool_properties = []
    role_tool_properties = []
    tool_name = []
    recommended_tool_ids = []

    for num in range(0,len(favoriate_tools)):
        current_favoriate = my_redis.get_tool_properties(favoriate_tools[num]) 
        favoriate_tool_properties.append(current_favoriate)
        current_favoriate_name = current_favoriate[2]
        print favoriate_tool_properties, current_favoriate_name
        temp = ''
        
        if num == 0:
            temp = engine_client.send_query({"items": [favoriate_tools[num]], "num": 2})
            recommended_tool_ids.append([current_favoriate_name, temp['itemScores'][0]['item']])
            recommended_tool_ids.append([current_favoriate_name, temp['itemScores'][1]['item']])
        else:
            temp = engine_client.send_query({"items": [favoriate_tools[num]], "num": 4})
            temp_id = [item[1] for item in recommended_tool_ids]
            for item in temp['itemScores']:
                if item['item'] not in temp_id:
                    print '%s not in %s' %(item['item'], temp_id)
                    recommended_tool_ids.append([current_favoriate_name, item['item']])
                    break
    for item in recommended_tool_ids:
        recommended_tool_properties.append([item[0],my_redis.get_tool_properties(item[1])])

    for tool in role_tools:
        role_tool_properties.append(my_redis.get_tool_properties(tool))

    tools = my_redis.get_tool_properties('tools')
    for tool in tools:
        name = my_redis.get_tool_properties(tool)[2]
        if '_' in name:
            name = name.replace('_',' ')
        tool_name.append(name)



    engine_client = predictionio.EngineClient(url="http://172.17.0.2:8001")
    hit_tools = []
    hits = engine_client.send_query({})
    temp = hits['itemScores']
    
    for num in range(0,6):
        if temp[num]['item'] != 'Surface':
            hit_tools.append([num, my_redis.get_tool_properties(temp[num]['item'])[2], my_redis.get_tool_properties(temp[num]['item'])[1]])
        

    print "hit_tools %s" %hit_tools


    # print 'favoriate_tool_properties%s'%favoriate_tool_properties
    return render_template('engine.html', username = username, favoriate_tools = favoriate_tool_properties, recommended_tool = recommended_tool_properties, role_tool = role_tool_properties, tool_name = tool_name, hit_tools=hit_tools,error = error)


# @app.route('/', methods = ['GET', 'POST'])
# def home():
#     return redirect(url_for('index'))


@app.route('/customer_list', methods = ['GET', 'POST'])
def getCustomerList():
    m_customers = my_redis.get_set("customer")
    return render_template('customer_list.html', customers = m_customers, error = error)

@app.route('/customer_project_list')
def getCustomerProject():
    param = request.url.__str__().rsplit('?')[1]
    m_customer = param.rsplit('=')[1]
    m_projects = my_redis.get_set(m_customer)
    return render_template('customer_project_list.html', customer=m_customer, projects=m_projects, error = error)

@app.route('/customer_node_list')
def getCustomerNode():
    params = request.url.__str__().rsplit('?')[1].rsplit('&')
    m_customer = params[0].rsplit('=')[1]
    m_project = params[1].rsplit('=')[1]
    m_nodes = my_redis.get_set(m_customer + m_project)
    m_active_node = m_nodes.pop()
    m_active_attrs = my_redis.get_hash(m_customer+m_project+m_active_node)
    m_dict = {}
    for node in m_nodes:
        m_dict[node] = my_redis.get_hash(m_customer+m_project+node)
    return render_template('customer_node_list2.html', customer=m_customer, project=m_project, nodes=m_dict,active_node=m_active_node, active_attrs=m_active_attrs, error =error)

@app.route('/api/dump', methods=['POST'], strict_slashes=False)
def dumpExcel():
    print("api_dump")
    params = request.url.__str__().rsplit('?')[1].rsplit('&')
    m_customer = params[0].rsplit('=')[1]
    m_project = params[1].rsplit('=')[1]
    m_ciqData = CiqData(m_customer, m_project)
    m_ciq = m_ciqData.fetch_ciq_from_redis()
    m_ciqData.dump_to_excel(m_ciq)
    return render_template('alert.html', message="Dump data to excel file successfully",error=error)

# @app.route('/customer_node_detail')
# def getNodeDetail():
#     params = request.url.__str__().rsplit('?')[1].rsplit('&')
#     m_customer = params[0].rsplit('=')[1]
#     m_project = params[1].rsplit('=')[1]
#     m_node = params[2].rsplit('=')[1]
#     m_attrs = my_redis.get_hash(m_customer + m_project + m_node)
#     return render_template('customer_node_detail.html', customer=m_customer, project=m_project, node=m_node, attrs=m_attrs,error =error)

@app.route('/customer_node_modify',methods=['POST'])
def modifyNodeDetail():
    params = request.url.__str__().rsplit('?')[1].rsplit('&')
   
    m_customer = params[0].rsplit('=')[1]
    m_project = params[1].rsplit('=')[1]
    m_node = params[2].rsplit('=')[1]
    m_attrs = my_redis.get_hash(m_customer + m_project + m_node)
    new_attrs ={}

    for key in m_attrs.keys():
        new_attrs[key] = request.form[m_node+key]
    my_redis.set_m_hash(new_attrs, m_customer + m_project + m_node)

    m_nodes = my_redis.get_set(m_customer+m_project)
    m_nodes.remove(m_node)
    m_dict = {}
    for node in m_nodes:
        m_dict[node] = my_redis.get_hash(m_customer+m_project+node)
    return render_template('customer_node_list2.html',customer=m_customer,project=m_project, nodes=m_dict,active_node=m_node, active_attrs=new_attrs, error=error)



# @app.route('/customer_project_detail')
# def getProjectInfo():
#     error = None
#     var_str = request.url.__str__().rsplit('?')
#     m_customer = var_str[1].rsplit('&')[0].rsplit('=')[1]
#     m_project = var_str[1].rsplit('&')[1].rsplit('=')[1]
#     #mtas = {"oam_vip":"10.0.0.10", "traffic_vip":"10.0.0.11"}
#     #sbg = {"mip": "10.0.0.12", "access_ip":"10.0.0.13"}
#     #m_ciq = {"mtas": mtas, "sbg":sbg}
#     m_ciq = my_redis.get_data(m_customer)[m_project]
#     return render_template('customer_project_detail.html', customer=m_customer, project=m_project, ciq=m_ciq, error = error)

@app.route('/alert')
def showAlert(message):
    m_message = message
    return render_template('alert.html', message=m_message, error = error)

@app.route('/create_project', methods = ['GET', 'POST'])
def createProject():
    error = None
    if request.method == 'POST':
        m_customer = request.form['customer']
        m_project = request.form['projectName']
        print("fetch customer from db")
        if m_customer == "" or m_project == "":
            error = 'customer and project name cannot be empty. Please try again.'
        elif (my_redis.is_member_set(m_project, m_customer)):
            error = "Project already exists under " + m_customer +", please try again"
            #return render_template('alert.html', message="Project already exists", error=None)
        else:
            return render_template('upload.html', customer_var=m_customer, project_var=m_project)

    return render_template('create_project.html', error = error)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/customer_project_upload', methods=['POST'])
def api_upload():
    #file_dir = os.path.join(basedir, m_customer)
    print("api_upload")
    params = request.url.__str__().rsplit('?')[1].rsplit('&')
    m_customer = params[0].rsplit('=')[1]
    m_project = params[1].rsplit('=')[1]
    print(m_customer)
    print(m_project)

    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f=request.files['myfile']

    if f and allowed_file(f.filename):
        fname=f.filename
        ext = fname.rsplit('.', 1)[1]
        unix_time = int(time.time())
        new_filename = str(unix_time)+'.'+ext
        f.save(os.path.join(file_dir, new_filename))
        
        my_ciq = CIQ_parser(os.path.join(file_dir, new_filename))
        my_ciq.parse_excel()
        my_redis.set_set(m_customer, "customer")
        my_redis.set_set(m_project, m_customer)
        for key,value in my_ciq.nodesConf.items():
            if bool(value):
                my_redis.set_set(key, m_customer+m_project)
                my_redis.set_m_hash(value, m_customer+m_project+key)

        m_nodes = my_ciq.nodesConf
        m_active_node,m_active_attrs = m_nodes.popitem()
        return render_template('customer_node_list2.html', customer=m_customer, project=m_project, nodes=m_nodes, active_node=m_active_node, active_attrs=m_active_attrs, error =error)

    else:
        return jsonify({"errno": 1001, "errmsg": "CIQ parse failed"})
#        return jsonify({"filename": f.filename})



 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
