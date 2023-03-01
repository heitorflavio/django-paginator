import requests
from django.core.paginator import Paginator
from django.shortcuts import render

def index(request):
    # URL da API do IBGE para listar estados
    url_estados = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome'

    # Obtém a lista de estados da API do IBGE
    response_estados = requests.get(url_estados)

    # Se a resposta for bem-sucedida (status code 200), obtém os dados da resposta
    if response_estados.status_code == 200:
        estados = response_estados.json()

        # Obtém o estado filtrado da query string ?state=
        estado_filtro = request.GET.get('state', None)

        # Se houver um estado filtrado, obtém o ID do estado a partir do seu nome
        if estado_filtro:
            estado = next((e for e in estados if e['sigla'].upper() == estado_filtro.upper()), None)
            if estado:
                url_cidades = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado["id"]}/municipios?orderBy=nome'
            else:
                # Se o estado filtrado não existir, exibe uma mensagem de erro
                error_message = f'Estado "{estado_filtro}" não encontrado'
                return render(request, 'mupi/error.html', {'message': error_message})
        else:
            # Se não houver um estado filtrado, lista todas as cidades
            url_cidades = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome'

        # Obtém a lista de cidades da API do IBGE
        response_cidades = requests.get(url_cidades)

        # Se a resposta for bem-sucedida (status code 200), obtém os dados da resposta
        if response_cidades.status_code == 200:
            cidades = response_cidades.json()

            # Ordena a lista de cidades por estado e nome da cidade
            cidades_sorted = sorted(cidades, key=lambda c: (c['microrregiao']['mesorregiao']['UF']['nome'], c['nome']))

            # Define a quantidade de registros por página

            registros = request.GET.get('registros_por_pagina', None)

            if registros:
                registros_por_pagina = int(registros)
            else:
                registros_por_pagina = 25

            # Cria um objeto Paginator com a lista de cidades e a quantidade de registros por página
            paginator = Paginator(cidades_sorted, registros_por_pagina)

            # Obtém o número da página atual a partir da query string ?page=
            page_number = request.GET.get('page')

            # Obtém a página atual com base no número da página
            page_obj = paginator.get_page(page_number)

            # Renderiza o template com a lista de cidades paginada
            context = {
                'page_obj': page_obj,
                'estados': estados,
                'selected_state': estado_filtro,
                'num_cidades': len(cidades),
                'registros_por_pagina': registros_por_pagina
            }
            return render(request, 'mupi/index.html', context)
        else:
            # Se a resposta não for bem-sucedida, exibe uma mensagem de erro
            error_message = f'Erro ao obter dados da API ({response_cidades.status_code})'
            return render(request, 'mupi/error.html', {'message': error_message})
    else:
        # Se a resposta não for bem-sucedida, exibe uma mensagem de erro
        error_message = f'Erro ao obter dados da API ({response_estados.status_code})'
        return render(request, 'mupi/error.html', {'message': error_message })
