from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

SCREENSHOTS_DIR = "/sessions/upbeat-intelligent-cori/screenshots"

def add_screenshot(story, filename, caption=None, width=5.5*inch):
    """Add a screenshot image to the story if the file exists."""
    path = os.path.join(SCREENSHOTS_DIR, filename)
    if os.path.exists(path):
        from PIL import Image as PILImage
        img = PILImage.open(path)
        iw, ih = img.size
        aspect = ih / iw
        img_width = width
        img_height = img_width * aspect
        # Cap height
        if img_height > 4*inch:
            img_height = 4*inch
            img_width = img_height / aspect
        story.append(Spacer(1, 8))
        story.append(RLImage(path, width=img_width, height=img_height))
        if caption:
            story.append(Paragraph(
                f"<i>{caption}</i>",
                ParagraphStyle('Caption', fontSize=9, textColor=HexColor('#6B7280'),
                               alignment=TA_CENTER, spaceAfter=10, spaceBefore=4)))
        story.append(Spacer(1, 8))

GREEN = HexColor('#8DAE10')
DARK = HexColor('#1F2937')
GRAY = HexColor('#6B7280')
LIGHT_BG = HexColor('#F8FAFC')
WHITE = HexColor('#FFFFFF')

def create_manual(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            topMargin=1*inch, bottomMargin=0.75*inch,
                            leftMargin=1*inch, rightMargin=1*inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
        fontSize=28, textColor=GREEN, spaceAfter=6, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=14, textColor=GRAY, spaceAfter=30, alignment=TA_CENTER)
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
        fontSize=18, textColor=DARK, spaceBefore=20, spaceAfter=10,
        fontName='Helvetica-Bold', borderColor=GREEN, borderWidth=0,
        borderPadding=0)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
        fontSize=14, textColor=GREEN, spaceBefore=14, spaceAfter=8,
        fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=11, textColor=DARK, spaceAfter=8, leading=16)
    note_style = ParagraphStyle('Note', parent=styles['Normal'],
        fontSize=10, textColor=GRAY, spaceAfter=6, leading=14,
        leftIndent=20, borderColor=GREEN, borderWidth=1,
        borderPadding=8, backColor=LIGHT_BG)
    step_style = ParagraphStyle('Step', parent=styles['Normal'],
        fontSize=11, textColor=DARK, spaceAfter=6, leading=16, leftIndent=20)

    story = []

    # ===== COVER PAGE =====
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("IntegrityMeter BI", title_style))
    story.append(Paragraph("Manual do Usuário", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="60%", thickness=3, color=GREEN, spaceAfter=20))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Plataforma de Gestão de Margem e Pipeline de Vendas",
        ParagraphStyle('CoverBody', parent=body_style, alignment=TA_CENTER, fontSize=12, textColor=GRAY)))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Versão 3.0 | Março 2026",
        ParagraphStyle('Version', parent=body_style, alignment=TA_CENTER, fontSize=10, textColor=GRAY)))
    story.append(PageBreak())

    # ===== TABLE OF CONTENTS =====
    story.append(Paragraph("Índice", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))
    toc_items = [
        "1. Primeiro Acesso",
        "2. Dashboard - Painel Principal",
        "3. Novo Negócio - Criar e Editar",
        "4. Pipeline de Vendas",
        "5. Relatórios e Exportação",
        "6. Histórico de Câmbio",
        "7. Painel Admin (Administradores)",
        "8. Dicas e Atalhos",
    ]
    for item in toc_items:
        story.append(Paragraph(item, ParagraphStyle('TOC', parent=body_style, fontSize=12, spaceAfter=10)))
    story.append(PageBreak())

    # ===== 1. PRIMEIRO ACESSO =====
    story.append(Paragraph("1. Primeiro Acesso", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    story.append(Paragraph("Ao receber este manual, você já possui uma conta criada pelo administrador.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Como entrar:", h2_style))
    steps = [
        'Clique no botão <b>"Acessar Plataforma"</b> no email de boas-vindas, ou acesse o link fornecido pelo administrador.',
        "Na tela de login, insira seu email e a senha temporária recebida.",
        "Clique em <b>Entrar</b>.",
        'No primeiro acesso, altere sua senha clicando em <b>"Alterar Senha"</b> na barra lateral.',
    ]
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {step}", step_style))

    add_screenshot(story, "01_login.png", "Tela de Login da plataforma", width=3.5*inch)

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Importante:</b> Altere sua senha temporária no primeiro acesso. "
        "Na barra lateral, clique no botão \"Alterar Senha\" ao lado do botão \"Sair\".", note_style))
    story.append(PageBreak())

    # ===== 2. DASHBOARD =====
    story.append(Paragraph("2. Dashboard - Painel Principal", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    story.append(Paragraph(
        "O Dashboard é a primeira tela após o login. Ele oferece uma visão geral "
        "completa do estado dos negócios.", body_style))

    add_screenshot(story, "02_dashboard.png", "Dashboard — Painel Principal com KPIs e alertas")

    story.append(Paragraph("KPIs (Indicadores Chave):", h2_style))
    kpi_data = [
        ['Indicador', 'Descrição'],
        ['Pipeline Ativo', 'Valor total dos negócios em andamento'],
        ['Total Ganho', 'Valor total dos negócios concluídos'],
        ['Lucro Total', 'Lucro acumulado de todos os negócios ganhos'],
        ['Negócios este Mês', 'Quantidade de negócios criados no mês atual'],
        ['Taxa Conversão', 'Percentual de negócios ganhos vs perdidos'],
        ['Margem Média', 'Margem média dos negócios concluídos'],
    ]
    t = Table(kpi_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Alertas Automáticos:", h2_style))
    story.append(Paragraph(
        "O sistema monitora automaticamente seus negócios e exibe alertas quando:", body_style))
    alerts = [
        "Um negócio está parado há mais de 7 dias (alerta amarelo).",
        "Um negócio está parado há mais de 14 dias (alerta vermelho).",
        "O dólar está acima de R$ 5,50 (sugestão de aguardar).",
        "O dólar está abaixo de R$ 4,80 (bom momento para fechar custos).",
    ]
    for a in alerts:
        story.append(Paragraph(f"- {a}", step_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Meta Mensal:", h2_style))
    story.append(Paragraph(
        "Defina uma meta de vendas mensal e acompanhe o progresso visualmente "
        "com a barra de progresso. O valor é editável a qualquer momento.", body_style))
    story.append(PageBreak())

    # ===== 3. NOVO NEGÓCIO =====
    story.append(Paragraph("3. Novo Negócio - Criar e Editar", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    story.append(Paragraph(
        "A aba <b>Novo Negócio</b> é o coração da plataforma. Use-a para criar novos negócios, "
        "editar negócios existentes e calcular a margem de lucro em tempo real.", body_style))
    story.append(Paragraph("- Calcular o lucro líquido de cada negócio em tempo real.", step_style))
    story.append(Paragraph("- Considerar custos em USD, câmbio ao vivo e impostos brasileiros.", step_style))
    story.append(Paragraph("- Salvar negócios no banco de dados para acompanhamento.", step_style))

    add_screenshot(story, "03_novo_negocio.png", "Aba Novo Negócio — formulário com tooltips e cálculo em tempo real")

    story.append(Spacer(1, 10))
    story.append(Paragraph("Como funciona:", h2_style))
    story.append(Paragraph(
        "Ao abrir a aba, você verá o formulário pronto para criar um novo negócio com a mensagem "
        "\"Preencha os dados abaixo para simular a margem e criar um novo negócio\". "
        "Ao clicar em um negócio existente na barra lateral, o formulário carrega os dados desse negócio "
        "e exibe \"Editando: [nome do cliente]\", com o botão mudando para <b>ATUALIZAR NEGÓCIO</b>.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Campos do Formulário:", h2_style))
    story.append(Paragraph(
        "Todos os campos possuem um ícone de ajuda (?) com explicação detalhada ao passar o mouse.", body_style))
    fields_data = [
        ['Campo', 'Descrição'],
        ['Cliente', 'Nome da empresa ou pessoa jurídica contratante'],
        ['Status', 'Fase atual do negócio no pipeline de vendas'],
        ['Qtd Testes', 'Quantidade de testes/avaliações a serem aplicados neste negócio'],
        ['Custo Unitário (USD)', 'Custo GA por teste pago ao fornecedor em dólares americanos'],
        ['Valor de Venda (R$)', 'Valor total cobrado do cliente em reais brasileiros'],
        ['Notas', 'Observações internas sobre o negócio (não visível ao cliente)'],
    ]
    t2 = Table(fields_data, colWidths=[2*inch, 4*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t2)

    story.append(Spacer(1, 15))
    story.append(Paragraph("Botões de Ação:", h2_style))
    actions_data = [
        ['Botão', 'Quando aparece', 'Função'],
        ['CRIAR NEGÓCIO', 'Formulário vazio (novo)', 'Salva um novo negócio no sistema'],
        ['ATUALIZAR NEGÓCIO', 'Editando negócio existente', 'Salva as alterações no negócio selecionado'],
        ['DUPLICAR', 'Apenas ao editar', 'Cria uma cópia do negócio atual como novo registro'],
        ['+ Novo Negócio', 'Barra lateral', 'Limpa o formulário para iniciar um novo negócio'],
    ]
    t_actions = Table(actions_data, colWidths=[1.5*inch, 1.8*inch, 2.7*inch])
    t_actions.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_actions)

    story.append(Spacer(1, 15))
    story.append(Paragraph("Fórmula de Cálculo:", h2_style))
    story.append(Paragraph("<b>Custo Total (BRL)</b> = Qtd Testes x Custo USD x Câmbio", body_style))
    story.append(Paragraph("<b>Impostos</b> = Venda x (Lucro Presumido % + Taxa Admin %)", body_style))
    story.append(Paragraph("<b>Lucro Líquido</b> = Venda - Custo Total BRL - Impostos", body_style))
    story.append(Paragraph("<b>Margem</b> = (Lucro / Venda) x 100", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Taxas configuráveis na barra lateral:", h2_style))
    tax_data = [
        ['Taxa', 'Descrição'],
        ['Lucro Presumido (%)', 'Alíquota do regime Lucro Presumido — imposto federal sobre o faturamento bruto'],
        ['Taxa Administração (%)', 'Taxa administrativa cobrada sobre o faturamento para custos operacionais'],
    ]
    t_tax = Table(tax_data, colWidths=[2*inch, 4*inch])
    t_tax.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_tax)

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Dica:</b> Os valores padrão de Lucro Presumido (16,33%) e Administração (2,50%) "
        "são editáveis na barra lateral. Ajuste conforme necessário.", note_style))
    story.append(PageBreak())

    # ===== 4. PIPELINE =====
    story.append(Paragraph("4. Pipeline de Vendas", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    story.append(Paragraph("O Pipeline mostra todos os negócios organizados por etapa.", body_style))

    add_screenshot(story, "04_pipeline.png", "Pipeline — negócios organizados por etapa com filtros")

    story.append(Paragraph("Etapas do Pipeline:", h2_style))
    stages_data = [
        ['Etapa', 'Cor', 'Descrição'],
        ['Proposta Enviada', 'Cinza', 'Proposta inicial enviada ao cliente'],
        ['Em Negociação', 'Azul', 'Em fase de negociação de valores/condições'],
        ['Aprovado', 'Verde', 'Cliente aprovou a proposta'],
        ['Contrato Assinado', 'Roxo', 'Contrato formalizado'],
        ['Em Execução', 'Amarelo', 'Testes sendo realizados'],
        ['Concluído', 'Verde escuro', 'Projeto entregue e finalizado'],
        ['Perdido', 'Vermelho', 'Negócio não concretizado'],
    ]
    t3 = Table(stages_data, colWidths=[1.8*inch, 1*inch, 3.2*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t3)

    story.append(Spacer(1, 15))
    story.append(Paragraph("Filtros:", h2_style))
    story.append(Paragraph(
        "Use os filtros no topo da aba Pipeline para encontrar negócios específicos:", body_style))
    story.append(Paragraph("- <b>Filtrar por Status:</b> selecione uma ou mais etapas.", step_style))
    story.append(Paragraph("- <b>Buscar Cliente:</b> digite parte do nome do cliente.", step_style))
    story.append(Paragraph("- <b>A partir de:</b> filtre por data de criação.", step_style))
    story.append(PageBreak())

    # ===== 5. RELATÓRIOS =====
    story.append(Paragraph("5. Relatórios e Exportação", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    story.append(Paragraph("Três tipos de relatório disponíveis:", body_style))

    add_screenshot(story, "05_relatorios.png", "Relatórios — KPIs, gráficos e exportação de dados")

    story.append(Spacer(1, 8))

    story.append(Paragraph("Negócios Concluídos:", h2_style))
    story.append(Paragraph(
        "Mostra apenas negócios finalizados com sucesso, com KPIs de faturamento, "
        "lucro e margem. Visualize por período (semanal, mensal, anual) com gráficos.", body_style))

    story.append(Paragraph("Rentabilidade por Cliente:", h2_style))
    story.append(Paragraph(
        "Ranking de clientes ordenados por lucro total. Veja quais clientes geram "
        "mais retorno, margem média e volume de testes.", body_style))

    story.append(Paragraph("Todos os Negócios:", h2_style))
    story.append(Paragraph(
        "Tabela completa com todos os negócios do sistema, independente do status.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Exportação:", h2_style))
    story.append(Paragraph(
        "Todos os relatórios podem ser exportados em formato CSV ou Excel. "
        "Clique nos botões <b>Baixar CSV</b> ou <b>Baixar Excel</b> no final de cada relatório.", body_style))
    story.append(PageBreak())

    # ===== 6. CÂMBIO =====
    story.append(Paragraph("6. Histórico de Câmbio", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    story.append(Paragraph(
        "Acompanhe a evolução do câmbio USD/BRL com gráficos interativos.", body_style))

    add_screenshot(story, "06_cambio.png", "Histórico de Câmbio — gráfico e simulação de impacto")

    story.append(Paragraph("- Visualize os últimos 7, 30 ou 90 dias.", step_style))
    story.append(Paragraph("- Veja mínimo, máximo e média do período.", step_style))
    story.append(Paragraph("- Simulação de impacto: como variações no câmbio afetam o lucro dos negócios ativos.", step_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Dica:</b> O câmbio é atualizado automaticamente a cada 15 minutos. "
        "Para forçar a atualização, clique no botão Att. na barra lateral.", note_style))
    story.append(PageBreak())

    # ===== 7. ADMIN =====
    story.append(Paragraph("7. Painel Admin", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    story.append(Paragraph(
        "Disponível apenas para usuários com papel de <b>Administrador</b>. "
        "Permite gerenciar todos os usuários e acompanhar a atividade do sistema.", body_style))

    add_screenshot(story, "07_admin.png", "Painel Admin — criar usuários e gerenciamento completo")

    story.append(Paragraph("Criar Usuários:", h2_style))
    story.append(Paragraph("1. Acesse a aba <b>Admin</b>.", step_style))
    story.append(Paragraph("2. Preencha nome completo, email e senha temporária.", step_style))
    story.append(Paragraph("3. Selecione o papel (<b>Usuário</b> ou <b>Admin</b>).", step_style))
    story.append(Paragraph("4. Marque a opção de enviar email de boas-vindas (recomendado).", step_style))
    story.append(Paragraph("5. Clique em <b>Criar Usuário</b>.", step_style))
    story.append(Paragraph(
        "O novo usuário receberá um email de boas-vindas com as credenciais, "
        "o manual em PDF anexado e um botão para acessar a plataforma.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Gerenciamento de Usuários:", h2_style))
    story.append(Paragraph(
        "Para cada usuário cadastrado, o administrador tem acesso a 5 ações:", body_style))
    mgmt_data = [
        ['Ação', 'Descrição'],
        ['Desativar / Reativar', 'Bloqueia ou libera o acesso do usuário à plataforma'],
        ['Resetar Senha', 'Define uma nova senha temporária para o usuário'],
        ['Reenviar Convite', 'Reenvia o email de boas-vindas com credenciais atualizadas'],
        ['Tornar Admin / Usuário', 'Altera o papel do usuário entre administrador e usuário comum'],
        ['Excluir', 'Remove permanentemente o usuário do sistema'],
    ]
    t_mgmt = Table(mgmt_data, colWidths=[2*inch, 4*inch])
    t_mgmt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_mgmt)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Log de Atividades:", h2_style))
    story.append(Paragraph(
        "Histórico completo de todas as mudanças de status nos negócios, "
        "incluindo quem alterou, quando e qual foi a mudança.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Importante:</b> Ações de gerenciamento não podem ser realizadas no próprio usuário logado, "
        "apenas em outros usuários do sistema.", note_style))
    story.append(PageBreak())

    # ===== 8. DICAS =====
    story.append(Paragraph("8. Dicas e Atalhos", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))

    tips = [
        "<b>Meus Negócios:</b> Na barra lateral, a seção \"Meus Negócios\" lista todos os seus negócios. Clique em qualquer um para carregá-lo no formulário e editá-lo.",
        "<b>Novo negócio:</b> Clique em \"+ Novo Negócio\" na barra lateral para limpar o formulário e iniciar um novo registro.",
        "<b>Duplicar:</b> Ao editar um negócio, use o botão <b>DUPLICAR</b> para criar uma cópia como novo registro.",
        "<b>Tooltips:</b> Passe o mouse sobre o ícone (?) ao lado de cada campo para ver uma explicação detalhada.",
        "<b>Cores de margem:</b> Verde = margem acima de 30%, Amarelo = 10-30%, Vermelho = abaixo de 10%.",
        "<b>Câmbio ao vivo:</b> O sistema busca o câmbio USD/BRL automaticamente. Use o botão Att. na barra lateral para atualizar.",
        "<b>Exportação:</b> Exporte dados em CSV ou Excel a qualquer momento na aba Relatórios.",
        "<b>Alterar senha:</b> Clique no botão \"Alterar Senha\" na barra lateral, ao lado do botão \"Sair\".",
        "<b>Busca rápida:</b> Use o campo de busca na barra lateral para encontrar negócios por nome de cliente.",
        "<b>Excluir negócio:</b> Na barra lateral, clique no botão X ao lado do negócio para removê-lo.",
    ]
    for tip in tips:
        story.append(Paragraph(f"- {tip}", step_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=15))
    story.append(Paragraph(
        "IntegrityMeter BI - Plataforma de Gestão de Margem",
        ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, fontSize=10, textColor=GRAY)))
    story.append(Paragraph(
        "Em caso de dúvidas, contate o administrador do sistema.",
        ParagraphStyle('Footer2', parent=body_style, alignment=TA_CENTER, fontSize=9, textColor=GRAY)))

    doc.build(story)
    print(f"Manual criado: {output_path}")

if __name__ == '__main__':
    create_manual('/sessions/upbeat-intelligent-cori/mnt/Desktop/IntegrityMeter_Manual.pdf')
