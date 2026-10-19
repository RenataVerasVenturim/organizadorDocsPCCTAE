from collections import defaultdict
from datetime import date
from pathlib import Path
import re
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import servidor as sv
from io import BytesIO
import subprocess
import sys

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

# Usa exatamente as pastas configuradas em servidor.py.
PASTA_DOCUMENTOS = sv.PASTA_DOCUMENTOS
PASTA_DADOS = sv.PASTA_DADOS

sv.preparar_armazenamento()

# Catálogo demonstrativo: ainda é necessário incluir os 55 critérios.
CRITERIOS = [
    # ============================================================
    # ANEXO I — REQUISITO I
    # ============================================================
    {
        "requisito": 1,
        "item": 1,
        "titulo": "Exercício do mandato como membro de conselhos superiores e conselhos de unidades e órgãos colegiados da Instituição Federal de Ensino",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 2,
        "titulo": "Coordenação ou presidência de núcleos, representações, grupos de trabalho ou similares, comissões ou comitês previstos no âmbito da administração pública, regularmente instituídos, ou reconhecidos pelo órgão ou pela entidade",
        "unidade": "Por designação",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 3,
        "titulo": "Participação como membro de núcleos, representações, grupos de trabalho ou similares, comissões ou comitês previstos no âmbito da administração pública, regularmente instituídos",
        "unidade": "Por designação",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 4,
        "titulo": "Participação como defensor dativo ou como membro de equipe designada em processos de apuração de materialidade e responsabilidade, como sindicância, processo administrativo disciplinar e tomada de contas especial",
        "unidade": "Por designação",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 5,
        "titulo": "Atuação em atividades de organização, fiscalização, execução de exame de seleção, vestibular ou concursos",
        "unidade": "Por designação",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 6,
        "titulo": "Atuação em atividades de elaboração, revisão e/ou correção de provas de exame de seleção, vestibular ou concursos",
        "unidade": "Por designação",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 7,
        "titulo": "Exercício de mandato em entidade sindical da categoria",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 1.5,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 8,
        "titulo": "Participação como membro em programas ou projetos de políticas públicas externas à Instituição Federal de Ensino, desde que comprovada a obtenção de resultados institucionais relevantes",
        "unidade": "Por designação",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 9,
        "titulo": "Representação legal da Instituição Federal de Ensino junto a órgãos e entidades do Poder Público ou responsabilidade técnica junto a órgãos de fiscalização, controle e regulação",
        "unidade": "Por designação",
        "pontos": 7.5,
        "variavel": False,
    },
    {
        "requisito": 1,
        "item": 10,
        "titulo": "Atuação técnica externa, formalmente autorizada ou reconhecida pela Instituição Federal de Ensino de lotação, em órgãos estatais ou paraestatais, escolas de governo, agências reguladoras ou organismos internacionais, com contribuição ou repercussão institucional",
        "unidade": "Por produto",
        "pontos": 4.5,
        "variavel": False,
    },

    # ============================================================
    # ANEXO II — REQUISITO II
    # ============================================================
    {
        "requisito": 2,
        "item": 1,
        "titulo": "Coordenação de projetos institucionais (ensino, pesquisa, extensão, gestão e inovação)",
        "unidade": "Por projeto",
        "pontos": 7.5,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 2,
        "titulo": "Participação em atividades técnicas e/ou especializadas em projetos, incluída a elaboração de projetos pedagógicos, programas e/ou ações institucionais (ensino, pesquisa, extensão, gestão e inovação)",
        "unidade": "Por projeto",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 3,
        "titulo": "Participação em comissão ou conselho editorial de livros, revistas ou publicações científicas ou outras publicações acadêmicas",
        "unidade": "Por mandato",
        "pontos": 7.5,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 4,
        "titulo": "Participação em atividade de Cooperação Técnica Interinstitucional em projetos institucionais",
        "unidade": "Por projeto",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 5,
        "titulo": "Participação em atividades de orientação, tutoria, preceptoria ou supervisão",
        "unidade": "Por designação",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 6,
        "titulo": "Participação em atividades de produção ou reformulação de material acessível, ou técnico de referência (manuais, roteiros técnicos)",
        "unidade": "Por produto",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 7,
        "titulo": "Participação em atividade de avaliação de trabalho ou atuação como jurado em eventos acadêmicos, científicos, culturais, esportivos e técnicos",
        "unidade": "Por evento",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 8,
        "titulo": "Participação em atividade institucional de produção audiovisual, artística, exposição, podcast ou outras formas de apresentação",
        "unidade": "Por projeto",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 9,
        "titulo": "Participação em programas de formação continuada e/ou ações de desenvolvimento de competências, desde que não utilizada para fins de aceleração da promoção na carreira (carga horária mínima de dez horas)",
        "unidade": "Por capacitação",
        "pontos": 1,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 10,
        "titulo": "Desempenho de atividade técnica especializada, formalmente reconhecida pela Instituição Federal de Ensino, com demonstração de domínio técnico diferenciado e contribuição institucional relevante na área de atuação",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 1,
        "variavel": False,
    },
    {
        "requisito": 2,
        "item": 11,
        "titulo": "Participação em capacitação, fórum, oficina, workshop e congresso, com carga horária mínima de dez horas, vinculada aos interesses da Instituição Federal de Ensino",
        "unidade": "Por evento",
        "pontos": 1,
        "variavel": False,
    },

    # ============================================================
    # ANEXO III — REQUISITO III
    # ============================================================
    {
        "requisito": 3,
        "item": 1,
        "titulo": "Recebimento de premiação de âmbito internacional por projeto implementado na administração pública",
        "unidade": "Por prêmio",
        "pontos": 20,
        "variavel": False,
    },
    {
        "requisito": 3,
        "item": 2,
        "titulo": "Recebimento de premiação de âmbito nacional por projeto implementado na administração pública",
        "unidade": "Por prêmio",
        "pontos": 15,
        "variavel": False,
    },
    {
        "requisito": 3,
        "item": 3,
        "titulo": "Recebimento de premiação de âmbito local ou institucional, formalmente instituído, por projeto implementado na administração pública",
        "unidade": "Por prêmio",
        "pontos": 7.5,
        "variavel": False,
    },

    # ============================================================
    # ANEXO IV — REQUISITO IV
    # ============================================================
    {
        "requisito": 4,
        "item": 1,
        "titulo": "Atuação tecnicamente qualificada na operação, na implantação, no suporte ou no apoio a desenvolvimento, parametrização ou aperfeiçoamento de sistemas estruturantes da administração pública",
        "unidade": "Por sistema",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 4,
        "item": 2,
        "titulo": "Elaboração de projeto básico ou de termo de referência, ou participação como membro de equipe de planejamento de contratação",
        "unidade": "Por designação",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 4,
        "item": 3,
        "titulo": "Exercício de atividades de gestão ou fiscalização de contratos de aquisição, serviços, convênios e acordos ou instrumentos correlatos",
        "unidade": "Por designação",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 4,
        "item": 4,
        "titulo": "Exercício de atividades relacionadas à licitação e às suas excepcionalidades",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 4,
        "item": 5,
        "titulo": "Participação em atividades de apoio técnico especializado em políticas, programas e ações de promoção na área de saúde humana, animal e ambiente, de acessibilidade ou diversidade, de interesse institucional",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 4,
        "item": 6,
        "titulo": "Atuação tecnicamente qualificada em ambientes ou processos que demandem condições especiais de segurança, cuidado ou conformidade com requisitos legais e regulatórios, desde que não receba adicional de periculosidade ou insalubridade em razão das mesmas condições",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 4,
        "item": 7,
        "titulo": "Atuação em sistemas e/ou processos de trabalho institucionais em ensino, pesquisa, extensão, gestão e inovação, desde que não constitua atividade habitual do cargo",
        "unidade": "Por designação",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 4,
        "item": 8,
        "titulo": "Atuação como responsável por setor ou por unidade, formalmente designado, desde que a designação não gere pagamento de remuneração",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 4.5,
        "variavel": False,
    },

    # ============================================================
    # ANEXO V — REQUISITO V
    # ============================================================
    {
        "requisito": 5,
        "item": 1,
        "titulo": "Exercício de cargo de direção (CD-02) ou equivalente",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 9,
        "pontos_substituto": 4.5,
        "variavel": True,
    },
    {
        "requisito": 5,
        "item": 2,
        "titulo": "Exercício de cargo de direção (CD-03 e 04) ou equivalente",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 7.5,
        "pontos_substituto": 3,
        "variavel": True,
    },
    {
        "requisito": 5,
        "item": 3,
        "titulo": "Exercício de função gratificada (FG-01 e 02) ou equivalente",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 4.5,
        "pontos_substituto": 1.5,
        "variavel": True,
    },
    {
        "requisito": 5,
        "item": 4,
        "titulo": "Exercício de função gratificada (a partir da FG-03) ou equivalente",
        "unidade": "Por ano ou fração acima de seis meses",
        "pontos": 3,
        "pontos_substituto": 1,
        "variavel": True,
    },

    # ============================================================
    # ANEXO VI — REQUISITO VI
    # ============================================================
    {
        "requisito": 6,
        "item": 1,
        "titulo": "Carta patente relacionada aos interesses institucionais",
        "unidade": "Por patente",
        "pontos": 30,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 2,
        "titulo": "Participação relevante no desenvolvimento de protótipos, depósitos e/ou registros de propriedade intelectual ou privilégio de invenção relacionada aos interesses institucionais",
        "unidade": "Por projeto",
        "pontos": 25,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 3,
        "titulo": "Participação em transferência de tecnologia, licenciamento ou exploração de ativo tecnológico, como autor ou inventor relacionada aos interesses institucionais",
        "unidade": "Por produto",
        "pontos": 20,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 4,
        "titulo": "Conclusão de curso de educação formal superior ao exigido para o ingresso no cargo de que é titular e que não seja utilizado para percepção de Incentivo à Qualificação – IQ",
        "unidade": "Por curso",
        "pontos": 15,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 5,
        "titulo": "Participação relevante na implantação ou desenvolvimento de produto, projeto, processo, técnica ou tecnologia de interesse institucional",
        "unidade": "Por produto",
        "pontos": 15,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 6,
        "titulo": "Atuação em atividade de liderança ou vice-liderança de grupo de pesquisa ou extensão registrado em órgão ou sistema oficial de reconhecimento institucional",
        "unidade": "Por grupo de pesquisa",
        "pontos": 7.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 7,
        "titulo": "Participação como membro em grupo de pesquisa devidamente registrado em órgão ou sistema oficial de reconhecimento institucional",
        "unidade": "Por projeto",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 8,
        "titulo": "Aprovação de projeto para a captação de recursos para a Instituição Federal de Ensino",
        "unidade": "Por projeto",
        "pontos": 7.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 9,
        "titulo": "Publicação ou organização de livro relacionado aos interesses institucionais (com ISBN e Conselho Editorial)",
        "unidade": "Por produto",
        "pontos": 20,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 10,
        "titulo": "Autoria ou coautoria de capítulo de livro, de artigo publicado em revista especializada, jornal científico ou periódico, relacionado aos interesses institucionais",
        "unidade": "Por publicação",
        "pontos": 7.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 11,
        "titulo": "Apresentação de trabalho de interesse institucional em congresso, seminário ou outros eventos",
        "unidade": "Por produto",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 12,
        "titulo": "Produção de material técnico, científico, metodológico ou administrativo estruturado que visa à difusão do conhecimento",
        "unidade": "Por produto",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 13,
        "titulo": "Avaliação do projeto de ensino e/ou pesquisa e/ou extensão e/ou inovação",
        "unidade": "Por projeto",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 14,
        "titulo": "Participação em atividade de difusão ou apoio à formação institucional (expositor, facilitador, colaborador)",
        "unidade": "Por evento",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 15,
        "titulo": "Atuação formalmente autorizada como instrutor, tutor, palestrante, autor de conteúdo técnico ou orientador em ação formativa estruturada de interesse institucional, prevista em plano ou programa de desenvolvimento de pessoas",
        "unidade": "Por curso",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 16,
        "titulo": "Atuação na coordenação de congresso, simpósio ou seminário de interesse institucional",
        "unidade": "Por evento",
        "pontos": 3.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 17,
        "titulo": "Exercício de atividade de coorientação de trabalho de conclusão de curso em diferentes modalidades de ensino",
        "unidade": "Por evento",
        "pontos": 4.5,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 18,
        "titulo": "Autoria de obra artística ou cultural registrada com contribuição ou repercussão institucional comprovada",
        "unidade": "Por produto",
        "pontos": 3,
        "variavel": False,
    },
    {
        "requisito": 6,
        "item": 19,
        "titulo": "Atuação institucional no enfrentamento de situações de surto, epidemia e pandemia",
        "unidade": "Por mês",
        "pontos": 1,
        "variavel": False,
    },
]


def obter_dados_formulario():
    """Lê os dados funcionais enviados pelo formulário."""
    return {
        "nome": request.form.get("nome", "").strip(),
        "nome_social": request.form.get("nome_social", "").strip(),
        "matricula_siape": request.form.get("matricula_siape", "").strip(),
        "cargo": request.form.get("cargo", "").strip(),
        "data_ingresso": request.form.get("data_ingresso", ""),
        "nivel_classificacao": request.form.get(
            "nivel_classificacao", ""
        ),
        "unidade_lotacao": request.form.get(
            "unidade_lotacao", ""
        ).strip(),

        "funcao_gratificada": (
            request.form.get("funcao_gratificada") == "Sim"
        ),
        "cargo_direcao": (
            request.form.get("cargo_direcao") == "Sim"
        ),

        "telefone": request.form.get("telefone", "").strip(),
        "email": request.form.get("email", "").strip(),

        "atendimento_prioritario": (
            request.form.get("atendimento_prioritario", "Não") == "Sim"
        ),
        "motivo_prioridade": request.form.get(
            "motivo_prioridade", ""
        ).strip(),

        "nivel_rsc_pretendido": request.form.get(
            "nivel_rsc_pretendido", ""
        ),

        # Dados de requerimento anterior (opcionais)
        "processo_anterior": request.form.get(
            "processo_anterior", ""
        ).strip(),

        "saldo_pontuacao_anterior": request.form.get(
            "saldo_pontuacao_anterior", ""
        ).strip(),
    }


def criar_dados_servidora(valores):
    """Converte os valores do formulário para o dataclass."""
    texto_data = valores.get("data_ingresso", "").strip()

    try:
        data_ingresso = (
            date.fromisoformat(texto_data) if texto_data else None
        )
    except ValueError:
        data_ingresso = None

    saldo_texto = str(
        valores.get("saldo_pontuacao_anterior", "")
    ).strip()

    try:
        if "," in saldo_texto:
            saldo_texto = saldo_texto.replace(".", "").replace(",", ".")

        saldo_anterior = float(saldo_texto) if saldo_texto else 0.0
    except ValueError:
        saldo_anterior = 0.0

    return sv.DadosServidor(
        nome=valores["nome"],
        nome_social=valores.get("nome_social", ""),
        matricula_siape=valores["matricula_siape"],
        cargo=valores["cargo"],
        data_ingresso=data_ingresso,
        nivel_classificacao=valores["nivel_classificacao"],
        unidade_lotacao=valores["unidade_lotacao"],
        funcao_gratificada=valores["funcao_gratificada"],
        cargo_direcao=valores["cargo_direcao"],
        telefone=valores["telefone"],
        email=valores["email"],
        atendimento_prioritario=valores["atendimento_prioritario"],
        motivo_prioridade=valores["motivo_prioridade"],
        nivel_rsc_pretendido=valores["nivel_rsc_pretendido"],
        processo_anterior=valores.get("processo_anterior", ""),
        saldo_pontuacao_anterior=saldo_anterior,
    )


def salvar_pdf(arquivo, requisito, item, ordem):
    """
    Salva um PDF no formato:
    requisito.item.ordemNomeOriginal.pdf

    O nome original é limitado a 50 caracteres,
    sem contar a extensão.
    """
    nome_original = secure_filename(arquivo.filename or "")

    if not nome_original:
        return None, "Nome de arquivo inválido."

    caminho_original = Path(nome_original)
    nome_base = caminho_original.stem[:50]
    extensao = caminho_original.suffix.lower()

    if extensao != ".pdf":
        return None, "A extensão do arquivo não é PDF."

    if not nome_base:
        return None, "Nome de arquivo inválido."

    conteudo = arquivo.read()

    if not conteudo:
        return None, "O arquivo está vazio."

    if len(conteudo) > sv.TAMANHO_MAXIMO_PDF:
        return None, "O arquivo excede o limite de 25 MB."

    if not conteudo.startswith(b"%PDF-"):
        return None, "O conteúdo não possui assinatura PDF válida."

    nome_final = f"{requisito}.{item}.{ordem}.{nome_base}{extensao}"
    destino = PASTA_DOCUMENTOS / nome_final

    if destino.exists():
        return None, (
            f"Já existe um arquivo com o nome {nome_final}. "
            "Verifique se há PDFs com nomes repetidos na mesma linha."
        )

    try:
        with destino.open("xb") as arquivo_destino:
            arquivo_destino.write(conteudo)
    except OSError as erro:
        return None, f"Não foi possível gravar o arquivo: {erro}"

    return nome_final, None

def converter_pontuacao(valor):
    """Converte números inteiros, decimais e decimais brasileiros."""
    if valor is None or valor == "":
        return 0.0

    texto = str(valor).strip()

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except (TypeError, ValueError):
        return 0.0


def obter_regras_rsc():
    """Mantém as mesmas regras configuradas no JavaScript."""
    return {
        "RSC-I": {
            "pontos": 10,
            "criterios": None,
            "requisitos_adicionais": [],
        },
        "RSC-II": {
            "pontos": 15,
            "criterios": 2,
            "requisitos_adicionais": [],
        },
        "RSC-III": {
            "pontos": 25,
            "criterios": 2,
            "requisitos_adicionais": [],
        },
        "RSC-IV": {
            "pontos": 30,
            "criterios": 3,
            "requisitos_adicionais": [2, 4, 5, 6],
        },
        "RSC-V": {
            "pontos": 52,
            "criterios": 5,
            "requisitos_adicionais": [4, 5, 6],
        },
        "RSC-VI": {
            "pontos": 75,
            "criterios": 7,
            "requisitos_adicionais": [6],
        },
    }


def montar_dados_requerimento(
    valores,
    pdfs_por_linha,
):
    """
    Monta os dados do requerimento a partir do catálogo e dos PDFs
    efetivamente salvos.

    pdfs_por_linha:
        {(requisito, item, numero_linha): [nomes dos PDFs salvos]}
    """

    nivel_informado = str(
        valores.get("nivel_rsc_pretendido", "")
    ).strip()

    nivel = nivel_informado.upper()

    if nivel and not nivel.startswith("RSC-"):
        nivel = f"RSC-{nivel}"

    regras = obter_regras_rsc()
    regra = regras.get(nivel)

    saldo_anterior = max(
        0.0,
        converter_pontuacao(
            valores.get("saldo_pontuacao_anterior")
        ),
    )

    # Agrupa os itens do catálogo em seus seis requisitos.
    criterios_json = []
    pontuacao_atual = 0.0
    criterios_comprovados = 0
    requisitos_comprovados = set()

    for requisito in range(1, 7):
        itens_json = []
        subtotal_requisito = 0.0

        itens_catalogo = [
            criterio
            for criterio in CRITERIOS
            if int(criterio["requisito"]) == requisito
        ]

        for criterio in itens_catalogo:
            numero_item = int(criterio["item"])
            linhas_json = []
            pontuacao_item = 0.0

            # Recupera todas as linhas de documentos desse item.
            chaves_linha = sorted(
                (
                    chave
                    for chave in pdfs_por_linha
                    if chave[0] == requisito
                    and chave[1] == numero_item
                ),
                key=lambda chave: chave[2],
            )

            for chave in chaves_linha:
                _, _, numero_linha = chave
                documentos = pdfs_por_linha[chave]

                # Cada linha representa uma ocorrência.
                # Mais de um PDF na mesma linha não multiplica a quantidade.
                quantidade = 1 if documentos else 0

                tipo_exercicio = str(
                    valores.get(
                        f"tipo_pontuacao__{requisito}_"
                        f"{numero_item}_{numero_linha}",
                        "titular",
                    )
                ).strip().lower()

                if tipo_exercicio not in {"titular", "substituto"}:
                    tipo_exercicio = "titular"

                pontos_unitarios = converter_pontuacao(
                    criterio["pontos"]
                )

                if criterio.get("variavel", False):
                    if tipo_exercicio == "substituto":
                        pontos_unitarios = converter_pontuacao(
                            criterio.get(
                                "pontos_substituto",
                                criterio["pontos"],
                            )
                        )

                pontos_linha = round(
                    quantidade * pontos_unitarios,
                    2,
                )

                pontuacao_item += pontos_linha

                linhas_json.append({
                    "numero_linha": numero_linha,
                    "tipo_exercicio": (
                        tipo_exercicio
                        if criterio.get("variavel", False)
                        else None
                    ),
                    "quantidade": quantidade,
                    "pontuacao_unitaria": pontos_unitarios,
                    "pontuacao_obtida": pontos_linha,
                    "documentos_comprobatorios": documentos,
                })

            pontuacao_item = round(pontuacao_item, 2)
            subtotal_requisito += pontuacao_item

            if pontuacao_item > 0:
                criterios_comprovados += 1
                requisitos_comprovados.add(requisito)

            itens_json.append({
                "numero_item": numero_item,
                "criterio_especifico": criterio["titulo"],
                "unidade_medida": criterio["unidade"],
                "pontuacao_unitaria_titular": converter_pontuacao(
                    criterio["pontos"]
                ),
                "pontuacao_unitaria_substituta": (
                    converter_pontuacao(
                        criterio["pontos_substituto"]
                    )
                    if criterio.get("variavel", False)
                    else None
                ),
                "variavel_por_tipo_exercicio": criterio.get(
                    "variavel", False
                ),
                "linhas_preenchidas": linhas_json,
                "pontuacao_obtida": pontuacao_item,
            })

        subtotal_requisito = round(subtotal_requisito, 2)
        pontuacao_atual += subtotal_requisito

        criterios_json.append({
            "numero_requisito": requisito,
            "itens": itens_json,
            "subtotal": subtotal_requisito,
        })

    pontuacao_atual = round(pontuacao_atual, 2)
    pontuacao_total = round(pontuacao_atual + saldo_anterior, 2)

    pontuacao_minima = regra["pontos"] if regra else None
    quantidade_minima = regra["criterios"] if regra else None
    requisitos_minimos = (
        regra["requisitos_adicionais"] if regra else []
    )

    pendencias = []

    if regra:
        if pontuacao_total < pontuacao_minima:
            pendencias.append({
                "tipo": "pontuacao",
                "descricao": "Pontuação mínima não atingida.",
                "pontos_faltantes": round(
                    pontuacao_minima - pontuacao_total,
                    2,
                ),
            })

        if (
            quantidade_minima is not None
            and criterios_comprovados < quantidade_minima
        ):
            pendencias.append({
                "tipo": "quantidade_criterios",
                "descricao": "Quantidade mínima de critérios não atingida.",
                "criterios_faltantes": (
                    quantidade_minima - criterios_comprovados
                ),
            })

        # Reproduz a regra do JavaScript: basta um dos requisitos adicionais.
        if requisitos_minimos and not any(
            requisito in requisitos_comprovados
            for requisito in requisitos_minimos
        ):
            pendencias.append({
                "tipo": "requisitos_adicionais",
                "descricao": (
                    "É necessário comprovar ao menos um dos requisitos "
                    "adicionais previstos para o nível."
                ),
                "requisitos_aceitos": requisitos_minimos,
            })

    return {
        "requerimento": {
            "nivel_rsc_pretendido": nivel_informado,
            "pontuacao_minima_necessaria": pontuacao_minima,
            "quantidade_criterios_minima": quantidade_minima,
            "quantidade_criterios_comprovados": criterios_comprovados,
            "requisitos_adicionais_exigidos": requisitos_minimos,
            "requisitos_comprovados": sorted(
                requisitos_comprovados
            ),
            "pontuacao_criterios_atuais": pontuacao_atual,
            "saldo_pontuacao_anterior": saldo_anterior,
            "pontuacao_total": pontuacao_total,
            "pontuacao_total_excedente": (
                round(max(0.0, pontuacao_total - pontuacao_minima), 2)
                if pontuacao_minima is not None
                else None
            ),
            "processo_anterior": valores.get(
                "processo_anterior", ""
            ),
            "pendencias": pendencias,
        },
        "criterios": criterios_json,
        "pontuacao_total": pontuacao_total,
    }
    
@app.route("/", methods=["GET", "POST"])
def index():
    mensagens = []
    sucesso = None

    if request.method == "POST":
        # 1. Esvazia as pastas antes de qualquer outro processamento.
        sv.limpar_armazenamento()

        # 2. Lê os dados e constrói o objeto do cadastro.
        valores = obter_dados_formulario()
        dados = criar_dados_servidora(valores)

        # 3. Valida os dados do cadastro.
        mensagens.extend(sv.validar(dados))

        # Confere a validade da data de ingresso.
        if valores["data_ingresso"] and dados.data_ingresso is None:
            mensagem_data = "Informe uma data de ingresso válida."
            if mensagem_data not in mensagens:
                mensagens.append(mensagem_data)

        # 4. Identifica os campos de arquivos associados a critérios válidos.
        criterios_validos = {
            (criterio["requisito"], criterio["item"])
            for criterio in CRITERIOS
        }

        campos_arquivo = []

        for chave in request.files.keys():
            correspondencia = re.fullmatch(
                r"pdf__(\d+)_(\d+)_(\d+)",
                chave,
            )

            if not correspondencia:
                continue

            requisito, item, numero_linha = map(
                int,
                correspondencia.groups(),
            )

            if (requisito, item) in criterios_validos:
                campos_arquivo.append(
                    (requisito, item, numero_linha, chave)
                )

        campos_arquivo.sort()

        # 5. Valida os PDFs em memória, sem gravá-los ainda.
        pdfs_validos = []
        erros_pdf = []

        for requisito, item, numero_linha, chave in campos_arquivo:
            for arquivo in request.files.getlist(chave):
                if not arquivo or not arquivo.filename:
                    continue

                nome_original = secure_filename(arquivo.filename)

                if not nome_original:
                    erros_pdf.append(
                        "Foi enviado um arquivo sem nome válido."
                    )
                    continue

                caminho_original = Path(nome_original)
                nome_base = caminho_original.stem[:50]
                extensao = caminho_original.suffix.lower()
                conteudo = arquivo.read()

                if extensao != ".pdf":
                    erros_pdf.append(
                        f"{arquivo.filename}: a extensão não é PDF."
                    )
                elif not nome_base:
                    erros_pdf.append(
                        f"{arquivo.filename}: nome inválido."
                    )
                elif not conteudo:
                    erros_pdf.append(
                        f"{arquivo.filename}: arquivo vazio."
                    )
                elif len(conteudo) > sv.TAMANHO_MAXIMO_PDF:
                    erros_pdf.append(
                        f"{arquivo.filename}: excede o limite de 25 MB."
                    )
                elif not conteudo.startswith(b"%PDF-"):
                    erros_pdf.append(
                        f"{arquivo.filename}: conteúdo PDF inválido."
                    )
                else:
                    pdfs_validos.append(
                        (
                            requisito,
                            item,
                            numero_linha,
                            nome_original,
                            conteudo,
                        )
                    )

        mensagens.extend(erros_pdf)

        # 6. Se houver erros, não grava os novos arquivos.
        # As pastas já foram esvaziadas no início do POST.
        if mensagens:
            return render_template(
                "index.html",
                criterios=CRITERIOS,
                mensagens=mensagens,
                sucesso=None,
            ), 400

         # 7. Grava os PDFs validados e registra quais foram salvos.
        total_salvos = 0
        pdfs_por_linha = {}

        for (
            requisito,
            item,
            numero_linha,
            nome_original,
            conteudo,
        ) in pdfs_validos:

            arquivo_memoria = BytesIO(conteudo)
            arquivo_memoria.filename = nome_original

            nome_salvo, erro = salvar_pdf(
                arquivo_memoria,
                requisito,
                item,
                numero_linha,
            )

            if erro:
                mensagens.append(f"{nome_original}: {erro}")
                continue

            chave_linha = (requisito, item, numero_linha)

            pdfs_por_linha.setdefault(chave_linha, []).append(
                nome_salvo
            )

            total_salvos += 1

        # 8. Monta os dados dos critérios e recalcula as pontuações.
        try:
            dados_adicionais = montar_dados_requerimento(
                valores=valores,
                pdfs_por_linha=pdfs_por_linha,
            )

            # Salva os campos cadastrais e os dados do requerimento
            # no mesmo arquivo JSON.
            sv.salvar_dados(
                dados,
                dados_adicionais=dados_adicionais,
            )

        except Exception as erro:
            mensagens.append(
                f"Erro ao salvar os dados do requerimento: {erro}"
            )

            return render_template(
                "index.html",
                criterios=CRITERIOS,
                mensagens=mensagens,
                sucesso=None,
            ), 500
                      # 9. Gera o requerimento HTML e depois compacta o dossiê.
        pasta_base = Path(__file__).resolve().parent

        scripts = [
            "gerar_requerimento.py",
            "compactar_dossie.py",
        ]

        try:
            for nome_script in scripts:
                caminho_script = pasta_base / nome_script

                if not caminho_script.is_file():
                    raise FileNotFoundError(
                        f"Script não encontrado: {caminho_script}"
                    )

                resultado = subprocess.run(
                    [sys.executable, str(caminho_script)],
                    cwd=str(pasta_base),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )

                print(f"\n===== {nome_script} =====")
                print("Saída:", resultado.stdout)
                print("Erros:", resultado.stderr)

                if resultado.returncode != 0:
                    raise RuntimeError(
                        f"Falha ao executar {nome_script}. "
                        "Consulte as mensagens no terminal."
                    )

            # 10. Verifica se o ZIP foi realmente criado.
            caminho_zip = (
                pasta_base
                / "processoArquivos"
                / "Dossie_RSC_PCCTAE.zip"
            )

            if not caminho_zip.is_file():
                raise FileNotFoundError(
                    f"O arquivo ZIP não foi encontrado: {caminho_zip}"
                )

            # 11. Envia o ZIP ao navegador como download.
            return send_file(
                caminho_zip,
                as_attachment=True,
                download_name="Dossie_RSC_PCCTAE.zip",
                mimetype="application/zip",
            )

        except (OSError, RuntimeError) as erro:
            mensagens.append(
                f"Erro ao gerar ou disponibilizar o dossiê: {erro}"
            )

            return render_template(
                "index.html",
                criterios=CRITERIOS,
                mensagens=mensagens,
                sucesso=None,
            ), 500
        # 9. Informa o resultado.
        sucesso = (
            f"Cadastro funcional e requerimento salvos em "
            f"{sv.ARQUIVO_DADOS}. "
            f"{total_salvos} PDF(s) salvo(s) em "
            f"{PASTA_DOCUMENTOS}.", 
            f"HTML gerado e dossiê compactado em ZIP."
        )
    return render_template(
        "index.html",
        criterios=CRITERIOS,
        mensagens=mensagens,
        sucesso=sucesso,
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
