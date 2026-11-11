"""
ADO-3 — Física: Práticas Extensivas
Opção B: colisão perfeitamente inelástica.

Dependências:
    pip install numpy matplotlib

Execução:
    python ADO3_Colisao_Inelastica.py

O programa usa as fórmulas fechadas do enunciado. Não há integração numérica.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

# ------------------------- Física -------------------------

def cinetica(m1, m2, v1, v2):
    """Energia cinética total, em joules."""
    return 0.5 * m1 * v1**2 + 0.5 * m2 * v2**2


def colisao_inelastica(m1, m2, v1, v2):
    """Retorna a velocidade comum após o choque e a variação de energia."""
    velocidade_comum = (m1 * v1 + m2 * v2) / (m1 + m2)
    delta_k = -0.5 * (m1 * m2 / (m1 + m2)) * (v1 - v2)**2
    return velocidade_comum, delta_k


def resultados(m1, m2, v1, v2, delta_t_ms):
    """Calcula momento, energia, impulsos e força média."""
    p_antes = m1 * v1 + m2 * v2
    k_antes = cinetica(m1, m2, v1, v2)
    V, delta_k_formula = colisao_inelastica(m1, m2, v1, v2)
    p_depois = (m1 + m2) * V
    k_depois = 0.5 * (m1 + m2) * V**2
    delta_k = k_depois - k_antes

    j1 = m1 * (V - v1)
    j2 = m2 * (V - v2)
    delta_t_s = max(delta_t_ms / 1000.0, 1e-9)
    forca_media = abs(j1) / delta_t_s

    return {
        "V": V, "p_antes": p_antes, "p_depois": p_depois,
        "k_antes": k_antes, "k_depois": k_depois,
        "delta_k": delta_k, "delta_k_formula": delta_k_formula,
        "j1": j1, "j2": j2, "forca_media": forca_media,
    }


# ------------------------- Interface -------------------------

class Simulacao:
    def __init__(self):
        self.m1, self.m2 = 2.0, 3.0
        self.v1, self.v2 = 5.0, 0.0
        self.delta_t_ms = 10.0
        self.tempo = 0.0
        self.pausado = False
        self.animacao = None

        self.fig = plt.figure(figsize=(13, 8))
        self.fig.canvas.manager.set_window_title(
            "ADO-3 — Colisão perfeitamente inelástica"
        )
        self.ax_anim = self.fig.add_axes([0.07, 0.48, 0.58, 0.43])
        self.ax_p = self.fig.add_axes([0.72, 0.72, 0.23, 0.18])
        self.ax_k = self.fig.add_axes([0.72, 0.49, 0.23, 0.18])
        self.ax_texto = self.fig.add_axes([0.68, 0.20, 0.30, 0.24])
        self.ax_texto.axis("off")

        self._criar_controles()
        self._desenhar_cena()
        self._atualizar_paineis()
        self._configurar_animacao()

    def _criar_controles(self):
        ax_m1 = self.fig.add_axes([0.10, 0.39, 0.43, 0.025])
        ax_m2 = self.fig.add_axes([0.10, 0.34, 0.43, 0.025])
        ax_v1 = self.fig.add_axes([0.10, 0.29, 0.43, 0.025])
        ax_v2 = self.fig.add_axes([0.10, 0.24, 0.43, 0.025])
        ax_dt = self.fig.add_axes([0.10, 0.19, 0.43, 0.025])

        self.s_m1 = Slider(ax_m1, "m1 (kg)", 0.5, 10, valinit=self.m1)
        self.s_m2 = Slider(ax_m2, "m2 (kg)", 0.5, 10, valinit=self.m2)
        self.s_v1 = Slider(ax_v1, "v1 (m/s)", -5, 10, valinit=self.v1)
        self.s_v2 = Slider(ax_v2, "v2 (m/s)", -5, 10, valinit=self.v2)
        self.s_dt = Slider(ax_dt, "Contato (ms)", 1, 100, valinit=self.delta_t_ms)

        self.s_m1.on_changed(self._controle_alterado)
        self.s_m2.on_changed(self._controle_alterado)
        self.s_v1.on_changed(self._controle_alterado)
        self.s_v2.on_changed(self._controle_alterado)
        self.s_dt.on_changed(self._controle_alterado)

        ax_pause = self.fig.add_axes([0.57, 0.29, 0.13, 0.055])
        ax_reset = self.fig.add_axes([0.57, 0.21, 0.13, 0.055])
        self.b_pause = Button(ax_pause, "Pausar")
        self.b_reset = Button(ax_reset, "Reiniciar")
        self.b_pause.on_clicked(self._alternar_pausa)
        self.b_reset.on_clicked(self._reiniciar)

    def _ler_controles(self):
        self.m1 = self.s_m1.val
        self.m2 = self.s_m2.val
        self.v1 = self.s_v1.val
        self.v2 = self.s_v2.val
        self.delta_t_ms = self.s_dt.val

    def _colisao_acontece(self):
        return self.v1 > self.v2

    def _tempo_colisao(self):
        # Distância inicial entre centros: 6 unidades.
        # Meias-larguras visuais somam 0.45*(sqrt(m1)+sqrt(m2)).
        # Soma das larguras dos dois blocos, conforme o desenho abaixo.
        largura_contato = 0.70 + 0.18 * (np.sqrt(self.m1) + np.sqrt(self.m2))
        distancia_livre = max(6.0 - largura_contato, 0.2)
        return distancia_livre / (self.v1 - self.v2)

    def _posicoes(self, t):
        x1_inicial, x2_inicial = -3.0, 3.0
        if not self._colisao_acontece():
            return x1_inicial + self.v1*t, x2_inicial + self.v2*t, False

        tc = self._tempo_colisao()
        if t <= tc:
            return x1_inicial + self.v1*t, x2_inicial + self.v2*t, False

        V = colisao_inelastica(self.m1, self.m2, self.v1, self.v2)[0]
        x_colisao = x1_inicial + self.v1*tc
        deslocamento = V * (t - tc)
        return x_colisao + deslocamento, x_colisao + deslocamento, True

    def _desenhar_cena(self):
        self.ax_anim.clear()
        self.ax_anim.set_xlim(-8, 8)
        self.ax_anim.set_ylim(-1.6, 2.0)
        self.ax_anim.set_yticks([])
        self.ax_anim.set_xlabel("Posição (unidades visuais)")
        self.ax_anim.set_title("Animação da colisão — movimento em uma dimensão")
        self.ax_anim.axhline(0, color="black", linewidth=1)

        x1, x2, unidos = self._posicoes(self.tempo)
        w1 = 0.35 + 0.18*np.sqrt(self.m1)
        w2 = 0.35 + 0.18*np.sqrt(self.m2)
        h1 = 0.45 + 0.12*np.sqrt(self.m1)
        h2 = 0.45 + 0.12*np.sqrt(self.m2)

        if unidos:
            largura = w1 + w2
            altura = max(h1, h2)
            self.ax_anim.add_patch(plt.Rectangle(
                (x1-largura/2, -altura/2), largura, altura,
                color="tab:purple", alpha=0.85
            ))
            self.ax_anim.text(x1, 0, "BLOCOS UNIDOS", color="white",
                              ha="center", va="center", weight="bold", fontsize=9)
        else:
            self.ax_anim.add_patch(plt.Rectangle(
                (x1-w1/2, -h1/2), w1, h1, color="tab:blue", alpha=0.85
            ))
            self.ax_anim.add_patch(plt.Rectangle(
                (x2-w2/2, -h2/2), w2, h2, color="tab:orange", alpha=0.85
            ))
            self.ax_anim.text(x1, 0, "1", color="white", ha="center", va="center",
                              weight="bold")
            self.ax_anim.text(x2, 0, "2", color="white", ha="center", va="center",
                              weight="bold")

        if self._colisao_acontece():
            tc = self._tempo_colisao()
            self.ax_anim.text(0.02, 0.94, f"Instante do choque: tc = {tc:.3f} s",
                              transform=self.ax_anim.transAxes, va="top")
        else:
            self.ax_anim.text(0.02, 0.94, "Sem colisão: v1 ≤ v2",
                              transform=self.ax_anim.transAxes, va="top",
                              color="red", weight="bold")

    def _atualizar_paineis(self):
        self.ax_p.clear()
        self.ax_k.clear()
        self.ax_texto.clear()
        self.ax_texto.axis("off")

        if not self._colisao_acontece():
            mensagem = (
                "NÃO HÁ COLISÃO\n\n"
                "A condição v1 > v2 não é satisfeita.\n"
                "Ajuste as velocidades nos controles."
            )
            self.ax_texto.text(0, 0.85, mensagem, color="red",
                               va="top", fontsize=11, weight="bold")
            self.ax_p.set_title("Momento total")
            self.ax_k.set_title("Energia cinética")
            self.ax_p.text(0.5, 0.5, "Sem colisão", ha="center")
            self.ax_k.text(0.5, 0.5, "Sem colisão", ha="center")
            return

        r = resultados(self.m1, self.m2, self.v1, self.v2, self.delta_t_ms)
        self.ax_p.bar(["Antes", "Depois"], [r["p_antes"], r["p_depois"]])
        self.ax_p.set_title("Momento linear total (kg·m/s)")
        self.ax_p.axhline(0, color="black", linewidth=0.7)

        self.ax_k.bar(["Antes", "Depois"], [r["k_antes"], r["k_depois"]])
        self.ax_k.set_title("Energia cinética total (J)")
        self.ax_k.axhline(0, color="black", linewidth=0.7)

        texto = (
            f"VELOCIDADES\n"
            f"Antes: v1 = {self.v1:.2f} | v2 = {self.v2:.2f} m/s\n"
            f"Depois: u1 = u2 = V = {r['V']:.2f} m/s\n\n"
            f"MOMENTO\n"
            f"Antes = {r['p_antes']:.2f} | Depois = {r['p_depois']:.2f} kg·m/s\n\n"
            f"ENERGIA\n"
            f"K antes = {r['k_antes']:.2f} J | K depois = {r['k_depois']:.2f} J\n"
            f"ΔK = {r['delta_k']:.2f} J\n\n"
            f"IMPULSO E FORÇA\n"
            f"J1 = {r['j1']:.2f} N·s | J2 = {r['j2']:.2f} N·s\n"
            f"F média = {r['forca_media']:.2f} N"
        )
        self.ax_texto.text(0, 1, texto, va="top", family="monospace", fontsize=8.6)

    def _controle_alterado(self, _):
        self._ler_controles()
        self.tempo = 0.0
        self._desenhar_cena()
        self._atualizar_paineis()
        self.fig.canvas.draw_idle()

    def _alternar_pausa(self, _):
        self.pausado = not self.pausado
        self.b_pause.label.set_text("Continuar" if self.pausado else "Pausar")
        if self.animacao is not None:
            if self.pausado:
                self.animacao.event_source.stop()
            else:
                self.animacao.event_source.start()

    def _reiniciar(self, _):
        self.tempo = 0.0
        self.pausado = False
        self.b_pause.label.set_text("Pausar")
        if self.animacao is not None:
            self.animacao.event_source.start()
        self._desenhar_cena()
        self.fig.canvas.draw_idle()

    def _configurar_animacao(self):
        def atualizar(_frame):
            if not self.pausado:
                self.tempo += 0.04
                self._desenhar_cena()
                self.fig.canvas.draw_idle()
            return []

        self.animacao = FuncAnimation(
            self.fig, atualizar, interval=40, blit=False, cache_frame_data=False
        )

    def mostrar(self):
        plt.show()


if __name__ == "__main__":
    Simulacao().mostrar()
