from flask import Flask, request
from flask_restful import Resource, Api
from models import Pessoas, Atividades, Usuarios
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

auth = HTTPBasicAuth()
app = Flask(__name__)
api = Api(app)

@auth.verify_password
def verificacao(login, senha):
  if not (login, senha):
    return False
  user = Usuarios.query.filter_by(login=login).first()
  if user is None or user.ativo == False:
    return False
  return check_password_hash(user.senha, senha)

class Pessoa(Resource):
  def get(self, nome):
    people = Pessoas.query.filter_by(nome=nome)
    person=[{'nome': p.nome, 'idade': p.idade, 'id': p.id} for p in people]
    if not len(person)==0:
      response = {
        'status':200,
        'pessoas':person
      }
    else:
      response = {
        'code': 404,
        'message':f'Nenhuma pessoa encontrada com o nome \'{nome}\'.'
      }
    return response
  
  @auth.login_required
  def put(self, nome):
    people = Pessoas.query.filter_by(nome=nome).first()
    
    if not 'nome' in people:
      return {'code': 404,'message':f'Nenhuma pessoa encontrada com o nome \'{nome}\'.'}
    
    try:
      dados = request.json
    except:
      return {'status':400, 'message':'JSON inválido.'}
    
    change = False
    if 'nome' in dados:
      people.nome = dados['nome']
      change = True
    if 'idade' in dados:
      people.idade = dados['idade']
      change = True
    
    if change:
      people.save()
      return {'status':200, 'pessoa':{
        'nome': people.nome,
        'idade': people.idade,
        'id': people.id
      }}
    else:
      return {'status':400, 'message':'Informe pelo menos o parâmetro \'nome\' ou \'idade\'.'}
  
  @auth.login_required
  def delete(self, nome):
    people = Pessoas.query.filter_by(nome=nome).first()
    try:
      nome = people.nome
      people.remove()
      return {'status':200, 'message':f'Pessoa \'{nome}\' excluída com sucesso.'}
    except AttributeError:
      return {'code': 404,'message':f'Nenhuma pessoa encontrada com o nome \'{nome}\'.'}

class Lista_Pessoas(Resource):
  def get(self):
    people = Pessoas.query.all()
    person=[{'nome': p.nome, 'idade': p.idade, 'id': p.id} for p in people]
    if not len(person)==0:
      response = {
        'status':200,
        'pessoas':person
      }
    else:
      response = {
        'code': 404,
        'message':'Nenhuma pessoa encontrada.'
      }
    return response

  @auth.login_required
  def post(self):
    try:
      dados = request.json
    except:
      return {'status':400, 'message':'JSON inválido.'}
    
    try:
      people = Pessoas(nome=dados['nome'], idade=dados['idade'])
      people.save()
      return {'status':200, 'pessoa':{
        'nome': people.nome,
        'idade': people.idade,
        'id': people.id
      }}
    except KeyError:
      return {'status':400, 'message':'Informe o parâmetro \'nome\' e \'idade\'.'}

class Lista_Atividades(Resource):
  def get(self):
    activity = Atividades.query.all()
    activities=[{'nome': a.nome, 'pessoa': a.pessoa.nome, 'id': a.id, 'finalizada': a.finalizada} for a in activity]
    if not len(activities)==0:
      response = {
        'status':200,
        'atividades': activities
      }
    else:
      response = {
        'code': 404,
        'message':'Nenhuma atividade encontrada.'
      }
    return response
  
  @auth.login_required
  def post(self):
    try:
      dados = request.json
    except:
      return {'status':400, 'message':'JSON inválido.'}
    
    try:
      people = Pessoas.query.filter_by(nome=dados['pessoa']).first()
    except KeyError:
      return {'status':400, 'message':'Informe o parâmetro \'pessoa\'.'}

    if people is None:
      return {'code': 404,'message':f'Nenhuma pessoa encontrada com o nome \'{dados["pessoa"]}\'.'}
    
    if 'finalizada' in dados:
      finalizada = True if dados['finalizada'] else False
    
    try:
      activity = Atividades(nome=dados['nome'], finalizada=finalizada, pessoa=people)
      activity.save()
      return {'status':200, 'pessoa':{
        'pessoa': activity.pessoa.nome,
        'atividad': activity.nome,
        'id': activity.id,
        'finalizada': activity.finalizada
      }}
    except KeyError:
      return {'status':400, 'message':'Informe o parâmetro \'nome\'.'}

class Atividade(Resource):
  def get(self, nome):
    person = Pessoas.query.filter_by(nome=nome).first()
    if person is None:
      return {'code': 404,'message':f'Nenhuma pessoa encontrada com o nome \'{nome}\'.'}
    activities = Atividades.query.filter_by(pessoa_id=person.id)
    activity = [{'nome': a.nome, 'pessoa': a.pessoa.nome, 'id': a.id, 'finalizada':a.finalizada} for a in activities]
    if len(activity)==0:
      return {'code': 404,'message':f'Nenhuma atividade encontrada para a pessoa \'{nome}\'.'}
    else:
      return {'code':200, 'atividades':activity}

class Uma_Atividade(Resource):
  def get(self, id):
    activity = Atividades.query.filter_by(id=id).first()
    if activity is None:
      return {'code': 404,'message':f'Nenhuma atividade encontrada com o id \'{id}\'.'}
    else:
      activities = {'nome': activity.nome, 'pessoa': activity.pessoa.nome, 'id': activity.id, 'finalizada':activity.finalizada}
      return {'atividade':activities}
  
  @auth.login_required
  def put(self, id):
    activity = Atividades.query.filter_by(id=id).first()
    if activity is None:
      return {'code': 404,'message':f'Nenhuma atividade encontrada com o id \'{id}\'.'}
    else:
      try:
        dados = request.json
      except:
        return {'status':400, 'message':'JSON inválido.'}
      if 'finalizada' in dados:
        finalizada = True if dados['finalizada'] else False
        activity.finalizada = finalizada
        activity.save()
        activities = {'nome': activity.nome, 'pessoa': activity.pessoa.nome, 'id': activity.id, 'finalizada':activity.finalizada}
        return {'status':200, 'atividade':activities}
      else:
        return {'status':400, 'message':'Informe o parâmetro \'finalizada\'.'}

api.add_resource(Pessoa, '/person/<string:nome>')
api.add_resource(Lista_Pessoas, '/person')
api.add_resource(Lista_Atividades, '/activities')
api.add_resource(Atividade, '/activities/<string:nome>')
api.add_resource(Uma_Atividade, '/activities/<int:id>')

app.run(debug=True)