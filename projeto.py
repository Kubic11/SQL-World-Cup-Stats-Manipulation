import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = db.execute('''
        SELECT * FROM
        (SELECT COUNT(*) n_mundiais FROM Mundiais)
        JOIN
        (SELECT COUNT(*) n_equipas FROM Equipas)
    ''').fetchone()

    return render_template('index.html',stats=stats)

@APP.route('/mundiais/')
def listar_mundiais():
    mundiais = db.execute('''
        SELECT ano, host, vencedor, segundo_lugar, terceiro_lugar, quarto_lugar
        FROM Mundiais
        ORDER BY ano ASC
    ''').fetchall()
    return render_template('listar_mundiais.html', mundiais=mundiais)


@APP.route('/equipas/')
def listar_equipas():
    equipas = db.execute('''
        SELECT e.idSigla, e.nome, COUNT(DISTINCT m.ano) n_participacoes from Partidas p
            natural join ocurrencias o
            natural join mundiais m
            join equipas e ON e.idSigla = p.sigla_eqcasa OR e.idSigla = p.sigla_eqfora
            group by e.idSigla
            order by n_participacoes DESC''').fetchall()
    return render_template('listar_equipas.html', equipas=equipas)

@APP.route('/mundiais/<ano>/')
def mundiais_ano(ano):
    participacoes = db.execute('''
        SELECT t1.n_partidas, t2.n_equipas FROM
            (SELECT COUNT(*) n_partidas, m.ano FROM Partidas p
            natural join Ocurrencias
            natural join Mundiais m
            WHERE m.ano = :ano
            GROUP BY m.ano) as t1
        JOIN    
            (SELECT COUNT(DISTINCT e.idSigla) as n_equipas, m.ano from Equipas e
            join Partidas p ON p.sigla_eqfora = e.idSigla OR p.sigla_eqcasa = e.idSigla
            natural join Ocurrencias
            natural join Mundiais m
            WHERE m.ano = :ano
            GROUP BY m.ano) as t2
    
        ON t1.ano = t2.ano;''', {'ano': ano}).fetchall()

    return render_template('mundiais_ano.html', ano=ano, participacoes=participacoes)

@APP.route('/mundiais/<ano>/partidas/')
def listar_partidas(ano):
    partidas = db.execute('''
        SELECT p.data, p.estadio, p.cidade, p.sigla_eqcasa, p.golos_eqcasa, p.golos_eqfora, p.sigla_eqfora, p.espectadores from Partidas p
        natural join ocurrencias o
        natural join mundiais m
        where m.ano = :ano
    ''', {'ano': ano}).fetchall()

    return render_template('listar_partidas.html', ano=ano, partidas=partidas)

@APP.route('/mundiais/<ano>/partidas/detalhes/')
def listar_detalhes(ano):
    detalhes = db.execute('''
        SELECT p.data, p.arbitro, p.assistente1, p.assistente2 from Partidas p
        natural join ocurrencias o
        natural join mundiais m
        where m.ano = :ano
    ''', {'ano': ano}).fetchall()

    return render_template('listar_detalhes.html', ano=ano, detalhes=detalhes)

@APP.route('/mundiais/<ano>/equipas_participantes/')
def listar_participantes(ano):
    participantes = db.execute('''
        SELECT e.idSigla, e.nome,
        SUM(CASE WHEN p.sigla_eqcasa = e.idSigla THEN p.golos_eqcasa ELSE p.golos_eqfora END) AS golos_marcados,
        SUM(CASE WHEN p.sigla_eqcasa = e.idSigla THEN p.golos_eqfora ELSE p.golos_eqcasa END) AS golos_sofridos
        FROM Equipas e NATURAL JOIN
        Participacoes pa NATURAL JOIN
        Mundiais m JOIN Partidas p ON (p.sigla_eqcasa = e.idSigla OR p.sigla_eqfora = e.idSigla)
        NATURAL JOIN Ocurrencias o
        WHERE m.ano = :ano
        GROUP BY e.idSigla
        ORDER BY golos_marcados DESC
    ''', {'ano': ano}).fetchall()

    return render_template('listar_participantes.html', ano=ano, participantes=participantes)