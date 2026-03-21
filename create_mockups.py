"""Create clean mockup diagrams of IntegrityMeter BI platform tabs."""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = "/sessions/upbeat-intelligent-cori/screenshots"
W, H = 900, 550
GREEN = (141, 174, 16)
DARK = (31, 41, 55)
GRAY = (107, 114, 128)
LIGHT_GRAY = (229, 231, 235)
WHITE = (255, 255, 255)
BG = (248, 250, 252)
BLUE = (59, 130, 246)
PURPLE = (139, 92, 246)
YELLOW = (234, 179, 8)
RED = (239, 68, 68)
DARK_GREEN = (5, 150, 105)

def get_font(size=14, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def draw_tab_bar(draw, active_idx=0):
    tabs = ["Dashboard", "Novo Negócio", "Pipeline", "Relatórios", "Câmbio", "Admin"]
    x = 50
    for i, tab in enumerate(tabs):
        font = get_font(12, bold=(i == active_idx))
        color = GREEN if i == active_idx else GRAY
        draw.text((x, 18), tab, fill=color, font=font)
        if i == active_idx:
            tw = font.getlength(tab)
            draw.line([(x, 36), (x + tw, 36)], fill=GREEN, width=2)
        x += font.getlength(tab) + 25

def draw_sidebar_hint(draw):
    # Sidebar area
    draw.rectangle([(0, 0), (40, H)], fill=(245, 247, 249))
    draw.line([(40, 0), (40, H)], fill=LIGHT_GRAY)

def draw_input_field(draw, x, y, w, label, value="", tooltip=True):
    font = get_font(11)
    font_sm = get_font(10)
    draw.text((x, y), label, fill=DARK, font=font)
    if tooltip:
        draw.ellipse([(x + font.getlength(label) + 5, y + 1), (x + font.getlength(label) + 17, y + 13)], outline=GRAY)
        draw.text((x + font.getlength(label) + 8, y + 1), "?", fill=GRAY, font=get_font(9))
    draw.rectangle([(x, y + 18), (x + w, y + 42)], outline=LIGHT_GRAY, fill=WHITE)
    if value:
        draw.text((x + 8, y + 23), value, fill=GRAY, font=font_sm)

def draw_button(draw, x, y, w, h, text, color=GREEN):
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=6, fill=color)
    font = get_font(12, bold=True)
    tw = font.getlength(text)
    draw.text((x + (w - tw) / 2, y + (h - 14) / 2), text, fill=WHITE, font=font)

def draw_kpi_card(draw, x, y, label, value, w=120):
    draw.rounded_rectangle([(x, y), (x + w, y + 60)], radius=8, outline=LIGHT_GRAY, fill=WHITE)
    font_sm = get_font(9)
    font_val = get_font(16, bold=True)
    lw = font_sm.getlength(label)
    draw.text((x + (w - lw) / 2, y + 8), label, fill=GRAY, font=font_sm)
    vw = font_val.getlength(value)
    draw.text((x + (w - vw) / 2, y + 28), value, fill=GREEN, font=font_val)

# ---- 3. Novo Negócio ----
def create_novo_negocio():
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_tab_bar(draw, active_idx=1)

    # Banner
    draw.rounded_rectangle([(50, 48), (850, 72)], radius=4, fill=(236, 253, 245))
    draw.text((60, 52), "Preencha os dados abaixo para simular a margem e criar um novo negócio.", fill=DARK_GREEN, font=get_font(11))

    # Form fields
    draw_input_field(draw, 50, 85, 280, "Cliente", "Nome da empresa")
    draw_input_field(draw, 350, 85, 280, "Status", "Proposta Enviada")
    draw_input_field(draw, 50, 145, 280, "Qtd Testes", "0")
    draw_input_field(draw, 350, 145, 280, "Custo Unitário (USD)", "0.00")
    draw_input_field(draw, 50, 205, 580, "Valor de Venda (R$)", "0.00")
    draw_input_field(draw, 50, 265, 580, "Notas", "", tooltip=True)

    # Right side - Lucro display
    draw.rounded_rectangle([(660, 85), (860, 200)], radius=8, outline=LIGHT_GRAY, fill=WHITE)
    draw.text((700, 95), "LUCRO LÍQUIDO", fill=GRAY, font=get_font(10))
    draw.text((690, 120), "R$ 0,00", fill=DARK, font=get_font(24, bold=True))
    draw.text((680, 155), "Preencha os dados", fill=GRAY, font=get_font(10))
    draw.text((690, 170), "para calcular", fill=GRAY, font=get_font(10))

    # Detalhamento
    draw.rounded_rectangle([(660, 215), (860, 245)], radius=6, outline=LIGHT_GRAY, fill=WHITE)
    draw.text((680, 222), "> Detalhamento do Cálculo", fill=DARK, font=get_font(10))

    # Button
    draw_button(draw, 660, 265, 200, 40, "CRIAR NEGÓCIO", GREEN)

    # Sidebar hint
    draw.rectangle([(0, 340), (40, H)], fill=(245, 247, 249))
    draw.text((3, 360), "MEUS", fill=GRAY, font=get_font(7))
    draw.text((0, 370), "NEGÓCIOS", fill=GRAY, font=get_font(7))

    img.save(f"{OUT}/03_novo_negocio.png")
    print("Created 03_novo_negocio.png")

# ---- 4. Pipeline ----
def create_pipeline():
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_tab_bar(draw, active_idx=2)

    draw.text((50, 50), "Pipeline de Vendas", fill=DARK, font=get_font(20, bold=True))

    # Filter bar
    draw.rounded_rectangle([(50, 85), (850, 115)], radius=6, fill=WHITE, outline=LIGHT_GRAY)
    draw.text((60, 92), "Filtrar por Status:", fill=GRAY, font=get_font(10))
    draw.text((180, 92), "Todos", fill=DARK, font=get_font(10))
    draw.text((350, 92), "Buscar Cliente:", fill=GRAY, font=get_font(10))
    draw.rectangle([(450, 90), (600, 112)], outline=LIGHT_GRAY, fill=WHITE)
    draw.text((650, 92), "A partir de:", fill=GRAY, font=get_font(10))

    # Pipeline columns
    stages = [
        ("Proposta Enviada", GRAY, 1),
        ("Em Negociação", BLUE, 0),
        ("Aprovado", DARK_GREEN, 0),
        ("Contrato Assinado", PURPLE, 1),
        ("Em Execução", YELLOW, 0),
        ("Concluído", (4, 120, 87), 2),
        ("Perdido", RED, 0),
    ]

    col_w = 110
    x = 50
    for name, color, count in stages:
        # Column header
        draw.rounded_rectangle([(x, 130), (x + col_w, 155)], radius=4, fill=color)
        font_sm = get_font(8, bold=True)
        tw = font_sm.getlength(name)
        tx = x + (col_w - tw) / 2
        draw.text((tx, 136), name, fill=WHITE, font=font_sm)

        # Count badge
        draw.text((x + col_w - 15, 160), str(count), fill=GRAY, font=get_font(10))

        # Deal cards
        for j in range(count):
            cy = 175 + j * 65
            draw.rounded_rectangle([(x + 3, cy), (x + col_w - 3, cy + 55)], radius=6, outline=LIGHT_GRAY, fill=WHITE)
            draw.text((x + 8, cy + 5), f"Cliente {j+1}", fill=DARK, font=get_font(9, bold=True))
            draw.text((x + 8, cy + 20), "R$ 8.500", fill=GREEN, font=get_font(9))
            draw.text((x + 8, cy + 35), "Margem: 45%", fill=GRAY, font=get_font(8))

        x += col_w + 5

    img.save(f"{OUT}/04_pipeline.png")
    print("Created 04_pipeline.png")

# ---- 5. Relatórios ----
def create_relatorios():
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_tab_bar(draw, active_idx=3)

    draw.text((50, 50), "Relatórios", fill=DARK, font=get_font(20, bold=True))

    # Sub-tabs
    for i, (name, active) in enumerate([("Negócios Concluídos", True), ("Rentabilidade por Cliente", False), ("Todos os Negócios", False)]):
        x = 50 + i * 220
        color = GREEN if active else GRAY
        draw.text((x, 85), name, fill=color, font=get_font(11, bold=active))
        if active:
            draw.line([(x, 102), (x + get_font(11, bold=True).getlength(name), 102)], fill=GREEN, width=2)

    # KPI cards
    draw_kpi_card(draw, 50, 115, "FATURAMENTO", "R$ 16.750", w=150)
    draw_kpi_card(draw, 215, 115, "LUCRO TOTAL", "R$ 8.207", w=150)
    draw_kpi_card(draw, 380, 115, "MARGEM MÉDIA", "46.4%", w=150)
    draw_kpi_card(draw, 545, 115, "NEGÓCIOS", "2", w=100)

    # Chart area
    draw.rounded_rectangle([(50, 195), (650, 400)], radius=8, outline=LIGHT_GRAY, fill=WHITE)
    draw.text((70, 205), "Faturamento por Período", fill=DARK, font=get_font(12, bold=True))
    # Simple bar chart
    bars = [(120, 200), (200, 280), (280, 150), (360, 320)]
    for bx, bh in bars:
        draw.rectangle([(bx, 380 - bh * 0.5), (bx + 50, 380)], fill=GREEN)

    # Export buttons
    draw_button(draw, 50, 420, 120, 32, "Baixar CSV", GRAY)
    draw_button(draw, 185, 420, 130, 32, "Baixar Excel", GREEN)

    # Table preview
    draw.rounded_rectangle([(50, 465), (850, 540)], radius=6, outline=LIGHT_GRAY, fill=WHITE)
    headers = ["Cliente", "Qtd Testes", "Venda (R$)", "Custo (R$)", "Lucro (R$)", "Margem"]
    hx = 60
    for h in headers:
        draw.text((hx, 472), h, fill=WHITE, font=get_font(9, bold=True))
        hx += 130
    draw.rectangle([(50, 465), (850, 490)], fill=GREEN)
    hx = 60
    for h in headers:
        draw.text((hx, 472), h, fill=WHITE, font=get_font(9, bold=True))
        hx += 130
    # Row
    draw.text((60, 500), "Gentil", fill=DARK, font=get_font(9))
    draw.text((190, 500), "50", fill=DARK, font=get_font(9))
    draw.text((320, 500), "14.000", fill=DARK, font=get_font(9))
    draw.text((450, 500), "6.961", fill=DARK, font=get_font(9))
    draw.text((580, 500), "7.039", fill=GREEN, font=get_font(9))
    draw.text((710, 500), "50.3%", fill=GREEN, font=get_font(9))

    img.save(f"{OUT}/05_relatorios.png")
    print("Created 05_relatorios.png")

# ---- 6. Câmbio ----
def create_cambio():
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_tab_bar(draw, active_idx=4)

    draw.text((50, 50), "Histórico de Câmbio USD/BRL", fill=DARK, font=get_font(20, bold=True))

    # Period selector
    for i, (name, active) in enumerate([("7 dias", False), ("30 dias", True), ("90 dias", False)]):
        x = 50 + i * 80
        if active:
            draw_button(draw, x, 85, 65, 28, name, GREEN)
        else:
            draw.rounded_rectangle([(x, 85), (x + 65, 113)], radius=6, outline=LIGHT_GRAY, fill=WHITE)
            draw.text((x + 10, 91), name, fill=GRAY, font=get_font(10))

    # Stats
    draw_kpi_card(draw, 320, 80, "MÍNIMO", "R$ 5.12", w=120)
    draw_kpi_card(draw, 455, 80, "MÁXIMO", "R$ 5.45", w=120)
    draw_kpi_card(draw, 590, 80, "MÉDIA", "R$ 5.32", w=120)

    # Chart area
    draw.rounded_rectangle([(50, 160), (850, 400)], radius=8, outline=LIGHT_GRAY, fill=WHITE)
    draw.text((70, 170), "Câmbio USD/BRL - Últimos 30 dias", fill=DARK, font=get_font(12, bold=True))
    # Line chart mockup
    import random
    random.seed(42)
    points = [(70 + i * 25, 300 - random.randint(20, 80)) for i in range(30)]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=GREEN, width=2)

    # Impact simulation
    draw.rounded_rectangle([(50, 415), (850, 530)], radius=8, outline=LIGHT_GRAY, fill=WHITE)
    draw.text((70, 425), "Simulação de Impacto no Câmbio", fill=DARK, font=get_font(14, bold=True))
    draw.text((70, 450), "Como variações no câmbio afetam o lucro dos seus negócios ativos:", fill=GRAY, font=get_font(11))

    scenarios = [("Câmbio +5%", RED, "-R$ 350"), ("Câmbio atual", DARK, "R$ 8.207"), ("Câmbio -5%", DARK_GREEN, "+R$ 350")]
    sx = 100
    for label, color, impact in scenarios:
        draw.text((sx, 480), label, fill=GRAY, font=get_font(10))
        draw.text((sx, 498), impact, fill=color, font=get_font(14, bold=True))
        sx += 250

    img.save(f"{OUT}/06_cambio.png")
    print("Created 06_cambio.png")

# ---- 7. Admin ----
def create_admin():
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_tab_bar(draw, active_idx=5)

    draw.text((50, 50), "Painel Administrativo", fill=DARK, font=get_font(20, bold=True))

    # Create user form
    draw.text((50, 85), "Criar Novo Usuário", fill=DARK, font=get_font(14, bold=True))
    draw.rounded_rectangle([(50, 105), (450, 250)], radius=8, outline=LIGHT_GRAY, fill=WHITE)
    draw_input_field(draw, 65, 115, 180, "Nome completo", tooltip=False)
    draw_input_field(draw, 260, 115, 175, "Email", tooltip=False)
    draw_input_field(draw, 65, 160, 180, "Senha temporária", tooltip=False)
    draw_input_field(draw, 260, 160, 175, "Papel", "user", tooltip=False)
    # Checkbox
    draw.rectangle([(65, 208), (77, 220)], outline=GREEN, fill=GREEN)
    draw.text((65, 208), "✓", fill=WHITE, font=get_font(10))
    draw.text((82, 208), "Enviar email de boas-vindas", fill=DARK, font=get_font(10))
    draw_button(draw, 65, 228, 130, 28, "Criar Usuário", GREEN)

    # User list
    draw.line([(50, 265), (850, 265)], fill=LIGHT_GRAY)
    draw.text((50, 275), "Usuários Cadastrados", fill=DARK, font=get_font(14, bold=True))

    # User cards
    users = [
        ("Ronen Ben Efraim", "ronen21@gmail.com", "Admin", True, True),
        ("Carlos Silva", "carlos@empresa.com", "Usuário", True, False),
        ("Ana Souza", "ana@empresa.com", "Usuário", False, False),
    ]

    y = 300
    for name, email, role, active, is_self in users:
        draw.rounded_rectangle([(50, y), (850, y + 65)], radius=8, outline=LIGHT_GRAY, fill=WHITE)
        draw.text((65, y + 8), name, fill=DARK, font=get_font(11, bold=True))
        draw.text((200, y + 8), f"| {email} | {role}", fill=GRAY, font=get_font(10))

        # Status badge
        sc = DARK_GREEN if active else RED
        st = "Ativo" if active else "Inativo"
        draw.rounded_rectangle([(770, y + 5), (830, y + 22)], radius=10, fill=(*sc, 30), outline=sc)
        draw.text((780, y + 7), st, fill=sc, font=get_font(9))

        # Action buttons (only for non-self users)
        if not is_self:
            btn_names = ["Desativar", "Resetar Senha", "Reenviar Convite", "Tornar Admin", "Excluir"]
            bx = 65
            for bn in btn_names:
                bw = get_font(9).getlength(bn) + 16
                draw.rounded_rectangle([(bx, y + 35), (bx + bw, y + 55)], radius=4, outline=LIGHT_GRAY, fill=WHITE)
                draw.text((bx + 8, y + 39), bn, fill=DARK, font=get_font(9))
                bx += bw + 8

        y += 75

    img.save(f"{OUT}/07_admin.png")
    print("Created 07_admin.png")

# Create all mockups
create_novo_negocio()
create_pipeline()
create_relatorios()
create_cambio()
create_admin()
print("All mockups created!")
