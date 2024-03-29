# -*- coding: cp1252 -*-
import sys
import util
import xml.etree.ElementTree

##########################
# XML PARSING PROCEDURES #
##########################

def get_complete_articles_from_cv(root, debug=False):
    outlet = []

    producao_bibliografica = root.find('PRODUCAO-BIBLIOGRAFICA')
    if producao_bibliografica is not None:
        artigos_publicados = producao_bibliografica.find('ARTIGOS-PUBLICADOS')
        todos_artigos = artigos_publicados.findall('ARTIGO-PUBLICADO')
        if todos_artigos is not None:
            for artigo_publicado in todos_artigos:
                dados_basicos = artigo_publicado.find('DADOS-BASICOS-DO-ARTIGO')
                if dados_basicos.attrib['NATUREZA'] == 'COMPLETO':
                    try:
                        outlet.append(int(dados_basicos.attrib['ANO-DO-ARTIGO']))
                    except ValueError:
                        if debug: print('oops!')
        else:
            if debug: print('Problems with {0}: no published articles'.format(cv))
    else:
        if debug: print('Problems with {0}: no bibliographic production'.format(cv))

    return outlet

def get_complete_conference_articles_from_cv(root, debug=False):
    outlet = []

    producao_bibliografica = root.find('PRODUCAO-BIBLIOGRAFICA')
    if producao_bibliografica is not None:
        artigos_publicados = producao_bibliografica.find('TRABALHOS-EM-EVENTOS')
        todos_artigos = artigos_publicados.findall('TRABALHO-EM-EVENTOS')
        if todos_artigos is not None:
            for artigo_publicado in todos_artigos:
                dados_basicos = artigo_publicado.find('DADOS-BASICOS-DO-TRABALHO')
                if dados_basicos.attrib['NATUREZA'] == 'COMPLETO':
                    try:
                        outlet.append(int(dados_basicos.attrib['ANO-DO-TRABALHO']))
                    except ValueError:
                        if debug: print('oops!')

        else:
            if debug: print('Problems with {0}: no published articles'.format(cv))
    else:
        if debug: print('Problems with {0}: no bibliographic production'.format(cv))

    return outlet

def get_book_chapters_from_cv(root, debug=False):
    outlet = []

    producao_bibliografica = root.find('PRODUCAO-BIBLIOGRAFICA')
    if producao_bibliografica is not None:
        livros_e_capitulos = producao_bibliografica.find('LIVROS-E-CAPITULOS')
        if livros_e_capitulos is not None:
            coisas_publicadas = livros_e_capitulos.find('CAPITULOS-DE-LIVROS-PUBLICADOS')
            if coisas_publicadas is not None:
                todos_capitulos = coisas_publicadas.findall('CAPITULO-DE-LIVRO-PUBLICADO')
                for capitulo in todos_capitulos:
                    dados_basicos = capitulo.find('DADOS-BASICOS-DO-CAPITULO')
                    outlet.append(int(dados_basicos.attrib['ANO']))
    else:
        if debug: print('Problems with {0}: no bibliographic production'.format(cv))

    return outlet

def get_works_from_cv(cv, debug=False):
    """
    Collect all works for a cv file and store in a dict relating every year to another dict,
    indicating how many items there are in each of the following categories:
    - "complete article"
    - "conference article"
    - "book chapter"
    """
    outlet = {}

    if debug: print('--- # {0}'.format(cv))
    root = None
    try:
        root = xml.etree.ElementTree.parse(cv).getroot()
    except Exception as e:
        if debug: print('Problems with {0}: {1}'.format(cv, e))
        return None
    outlet["complete article"] = get_complete_articles_from_cv(root, debug)
    outlet["conference article"] = get_complete_conference_articles_from_cv(root, debug)
    outlet["book chapter"] = get_book_chapters_from_cv(root, debug)

    return outlet

def get_name_from_cv(cv, debug):
    outlet = {}

    if debug: print('--- # {0}'.format(cv))
    root = None
    try:
        root = xml.etree.ElementTree.parse(cv).getroot()
    except Exception as e:
        if debug: print('Problems with {0}: {1}'.format(cv, e))
        return None
    return root.getchildren()[0].attrib['NOME-COMPLETO']

##################
# MAIN FUNCTIONS #
##################

def get_output(config):
    cv_folder = config['working'] + config['cv dir']
    return cv_folder + 'works.csv'

def store_production_by_kind(config, works):
    # counting kinds by year
    kinds_by_year = {}
    kinds = set()
    for name in works:
        for kind in works[name]:
            for year in works[name][kind]:
                if year not in kinds_by_year:
                    kinds_by_year[year] = {}
                if kind not in kinds_by_year[year]:
                    kinds_by_year[year][kind] = 0
                    kinds.add(kind)
                kinds_by_year[year][kind] += 1

    print(kinds_by_year)
    # saving table
    years = sorted(list(kinds_by_year.keys()))
    with open(get_output(config), 'w') as outlet:
        line = 'type'
        for year in years:
            line += '\t{0}'.format(year)
        outlet.write('{0}\n'.format(line))
        for kind in kinds:
            line = kind
            for year in years:
                if kind in kinds_by_year[year]:
                    line += '\t{0}'.format(kinds_by_year[year][kind])
                else:
                    line += '\t0'
            outlet.write('{0}\n'.format(line))

def unpack_works_from_all_cv(all_cv, debug=False):
    outlet = {}

    for cv in all_cv:
        stuff = get_works_from_cv(cv, debug)
        if stuff is not None:
            outlet[get_name_from_cv(cv, debug)] = stuff

    return outlet

def unpack_works(config):
    cv_folder = config['working'] + config['cv dir']
    all_cv = util.get_all_files(cv_folder)
    works = unpack_works_from_all_cv(all_cv)
    return works

if __name__ == '__main__':
    config = util.load_config(sys.argv[1])
    works = unpack_works(config)
    print(works)
