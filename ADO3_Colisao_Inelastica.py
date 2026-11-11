"""
ADO-3 — Física: Práticas Extensivas
Opção B — colisão perfeitamente inelástica.

Requisitos atendidos:
- FuncAnimation para movimento retilíneo uniforme antes/depois do choque;
- sliders m1, m2, v1, v2 e duração do contato;
- botões Pausar/Continuar e Reiniciar;
- painel de resultados e gráficos de p e K;
- aviso quando v1 <= v2 (não ocorre colisão).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button


def cinetica(m1, m2, v1, v2):
    """Energia cinética total em joules."""
    return 0.5 * m1 * v1**2 + 0.5 * m2 * v2**2


def colisao_inelastica(m1, m2, v1, v2):
    """Velocidade comum após a colisão perfeitamente inelástica."""
    V = (m1 * v1 + m2 * v2) / (m1 + m2)
    mu = (m1 * m2) / (m1 + m2)
    delta_k = -0.5 * mu * (v1 - v2)**2
    return V, delta_k


def calcular_resultados(m1, m2, v1, v2, delta_t_ms):
    V, delta_k_formula = colisao_inelastica(m1, m2, v1, v2)
    p_antes = m1*v1 + m2*v2
    p_depois = (m1+m2)*V
    k_antes = cinetica(m1, m2, v1, v2)
    k_depois = 0.5*(m1+m2)*V**2
    J1 = m1*(V-v1)
    J2 = m2*(V-v2)
    dt = delta_t_ms/1000.0
    return dict(V=V, p_antes=p_antes, p_depois=p_depois,
                k_antes=k_antes, k_depois=k_depois,
                delta_k=k_depois-k_antes,
                delta_k_formula=delta_k_formula,
                J1=J1, J2=J2, Fmedia=abs(J1)/dt)


class Simulacao:
    def __init__(self):
        self.m1, self.m2 = 2.0, 3.0
        self.v1, self.v2 = 5.0, 0.0
        self.delta_t_ms = 10.0
        self.tempo = 0.0
        self.pausado = False
        self.anim = None

        self.fig = plt.figure(figsize=(13, 8))
        self.fig.canvas.manager.set_window_title("ADO-3 — Colisão perfeitamente inelástica")
        self.ax_anim = self.fig.add_axes([0.07, 0.50, 0.58, 0.42])
        self.ax_p = self.fig.add_axes([0.72, 0.73, 0.23, 0.17])
        self.ax_k = self.fig.add_axes([0.72, 0.51, 0.23, 0.17])
        self.ax_info = self.fig.add_axes([0.68, 0.17, 0.30, 0.29])
        self.ax_info.axis("off")
        self._criar_controles()
        self._atualizar_tudo()
        self.anim = FuncAnimation(self.fig, self._frame, interval=40,
                                  blit=False, cache_frame_data=False)

    def _criar_controles(self):
        axes = [
            self.fig.add_axes([0.10, 0.40, 0.43, 0.025]),
            self.fig.add_axes([0.10, 0.35, 0.43, 0.025]),
            self.fig.add_axes([0.10, 0.30, 0.43, 0.025]),
            self.fig.add_axes([0.10, 0.25, 0.43, 0.025]),
            self.fig.add_axes([0.10, 0.20, 0.43, 0.025]),
        ]
        self.s_m1 = Slider(axes[0], "m1 (kg)", 0.5, 10, valinit=self.m1)
        self.s_m2 = Slider(axes[1], "m2 (kg)", 0.5, 10, valinit=self.m2)
        self.s_v1 = Slider(axes[2], "v1 (m/s)", -5, 10, valinit=self.v1)
        self.s_v2 = Slider(axes[3], "v2 (m/s)", -5, 10, valinit=self.v2)
        self.s_dt = Slider(axes[4], "Contato (ms)", 1, 100, valinit=self.delta_t_ms)
        for slider in (self.s_m1, self.s_m2, self.s_v1, self.s_v2, self.s_dt):
            slider.on_changed(self._controle_alterado)

        self.b_pause = Button(self.fig.add_axes([0.57, 0.31, 0.13, 0.055]), "Pausar")
        self.b_reset = Button(self.fig.add_axes([0.57, 0.23, 0.13, 0.055]), "Reiniciar")
        self.b_pause.on_clicked(self._pausar)
        self.b_reset.on_clicked(self._reiniciar)

    def _ler(self):
        self.m1, self.m2 = self.s_m1.val, self.s_m2.val
        self.v1, self.v2 = self.s_v1.val, self.s_v2.val
        self.delta_t_ms = self.s_dt.val

    def _larguras(self):
        # Dimensão física ilustrativa em metros, proporcional à raiz da massa.
        return 0.6*np.sqrt(self.m1), 0.6*np.sqrt(self.m2)

    def _estado(self):
        w1, w2 = self._larguras()
        # Distância inicial livre entre as faces: 6 m.
        distancia_centros = 6.0 + (w1+w2)/2
        x10, x20 = -distancia_centros/2, distancia_centros/2
        ocorre = self.v1 > self.v2
        tc = 6.0/(self.v1-self.v2) if ocorre else None
        r = calcular_resultados(self.m1, self.m2, self.v1, self.v2,
                                self.delta_t_ms) if ocorre else None
        return w1, w2, x10, x20, ocorre, tc, r

    def _posicoes(self, t):
        w1, w2, x10, x20, ocorre, tc, r = self._estado()
        x1 = x10 + self.v1*t
        x2 = x20 + self.v2*t
        unidos = False
        if ocorre and t >= tc:
            x1c = x10 + self.v1*tc
            x2c = x20 + self.v2*tc
            x1 = x1c + r["V"]*(t-tc)
            x2 = x2c + r["V"]*(t-tc)
            unidos = True
        return x1, x2, unidos

    def _desenhar_animacao(self):
        self.ax_anim.clear()
        w1, w2, x10, x20, ocorre, tc, r = self._estado()
        x1, x2, unidos = self._posicoes(self.tempo)
        # Mostra todo o percurso da animação; o tempo é limitado após o choque.
        fim = (tc + 2.0) if ocorre else 2.0
        amostras = [x10, x20, x1, x2]
        if ocorre:
            amostras += [x10+self.v1*tc+r["V"]*2,
                         x20+self.v2*tc+r["V"]*2]
        margem = max(2.0, (w1+w2))
        xmin, xmax = min(amostras)-margem, max(amostras)+margem
        if xmax-xmin < 8:
            centro=(xmin+xmax)/2
            xmin,xmax=centro-4,centro+4
        self.ax_anim.set_xlim(xmin, xmax)
        self.ax_anim.set_ylim(-1.6, 1.8)
        self.ax_anim.set_yticks([])
        self.ax_anim.set_xlabel("Posição (m)")
        self.ax_anim.set_title("Movimento retilíneo uniforme antes e depois do choque")
        self.ax_anim.axhline(0, color="black", linewidth=1)
        h1, h2 = 0.45+0.12*np.sqrt(self.m1), 0.45+0.12*np.sqrt(self.m2)
        self.ax_anim.add_patch(plt.Rectangle((x1-w1/2, -h1/2), w1, h1,
                                             color="tab:blue"))
        self.ax_anim.add_patch(plt.Rectangle((x2-w2/2, -h2/2), w2, h2,
                                             color="tab:orange"))
        self.ax_anim.text(x1, 0, "1", color="white", ha="center", va="center", weight="bold")
        self.ax_anim.text(x2, 0, "2", color="white", ha="center", va="center", weight="bold")
        if ocorre:
            fase = "APÓS O CHOQUE: blocos unidos" if unidos else "ANTES DO CHOQUE"
            self.ax_anim.text(0.02, 0.94, f"{fase} | tc = {tc:.3f} s",
                              transform=self.ax_anim.transAxes, va="top")
            self.ax_anim.text(0.02, 0.86,
                              f"v1 = {self.v1:.2f} m/s | v2 = {self.v2:.2f} m/s",
                              transform=self.ax_anim.transAxes, va="top")
            if unidos:
                self.ax_anim.text(0.02, 0.78, f"u1 = u2 = V = {r['V']:.2f} m/s",
                                  transform=self.ax_anim.transAxes, va="top")
        else:
            self.ax_anim.text(0.02, 0.94, "SEM COLISÃO: v1 ≤ v2",
                              transform=self.ax_anim.transAxes, va="top", color="red")

    def _atualizar_paineis(self):
        self.ax_p.clear(); self.ax_k.clear(); self.ax_info.clear()
        self.ax_info.axis("off")
        w1,w2,x10,x20,ocorre,tc,r=self._estado()
        if not ocorre:
            self.ax_p.set_title("Momento linear total")
            self.ax_k.set_title("Energia cinética total")
            self.ax_info.text(0,0.9,
                "NÃO OCORRE COLISÃO\n\nA condição v1 > v2 não é satisfeita.\n"
                "Os blocos seguem em MRU sem se tocar.",
                color="red",va="top",fontsize=11)
            return
        self.ax_p.bar(["Antes","Depois"],[r["p_antes"],r["p_depois"]])
        self.ax_p.set_title("Momento total (kg·m/s)")
        self.ax_p.axhline(0,color="black",linewidth=.6)
        self.ax_k.bar(["Antes","Depois"],[r["k_antes"],r["k_depois"]])
        self.ax_k.set_title("Energia cinética total (J)")
        self.ax_k.axhline(0,color="black",linewidth=.6)
        texto=(
            f"VELOCIDADES\nAntes: v1={self.v1:.2f}; v2={self.v2:.2f} m/s\n"
            f"Depois: u1=u2=V={r['V']:.2f} m/s\n"
            f"Instante do choque: tc={tc:.3f} s\n\n"
            f"MOMENTO\nAntes={r['p_antes']:.2f}; Depois={r['p_depois']:.2f} kg·m/s\n\n"
            f"ENERGIA\nK antes={r['k_antes']:.2f}; K depois={r['k_depois']:.2f} J\n"
            f"Delta K={r['delta_k']:.2f} J\n\n"
            f"IMPULSO E FORÇA\nJ1={r['J1']:.2f}; J2={r['J2']:.2f} N·s\n"
            f"Força média={r['Fmedia']:.2f} N"
        )
        self.ax_info.text(0,1,texto,va="top",family="monospace",fontsize=8.2)

    def _atualizar_tudo(self):
        self._desenhar_animacao()
        self._atualizar_paineis()
        self.fig.canvas.draw_idle()

    def _controle_alterado(self, _):
        self._ler()
        self.tempo=0.0
        self.pausado=False
        self.b_pause.label.set_text("Pausar")
        self._atualizar_tudo()
        if self.anim is not None:
            self.anim.event_source.start()

    def _pausar(self, _):
        self.pausado=not self.pausado
        self.b_pause.label.set_text("Continuar" if self.pausado else "Pausar")

    def _reiniciar(self, _):
        self.tempo=0.0
        self.pausado=False
        self.b_pause.label.set_text("Pausar")
        self._atualizar_tudo()

    def _frame(self, _):
        if not self.pausado:
            self.tempo += 0.04
            w1,w2,x10,x20,ocorre,tc,r=self._estado()
            if ocorre and self.tempo > tc+2.0:
                self.tempo=tc+2.0
                self.pausado=True
                self.b_pause.label.set_text("Continuar")
            self._atualizar_tudo()
        return []

    def mostrar(self):
        plt.show()


if __name__ == "__main__":
    Simulacao().mostrar()
