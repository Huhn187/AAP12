# -*- coding: utf-8 -*-
import random
import tkinter as tk
from tkinter import ttk

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
BET_OPTIONS = [10, 20, 50, 100, 200, 500]
STARTING_BALANCE = 1000
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 16

class Player:
    def __init__(self, index):
        self.index = index
        self.name = f'Spieler {index + 1}'
        self.balance = STARTING_BALANCE
        self.bet = BET_OPTIONS[0]
        self.hand = []
        self.blackjack = False
        self.active = False
        self.status = 'Bereit'

    def reset_hand(self):
        self.hand = []
        self.blackjack = False
        self.status = 'Bereit'

    def can_bet(self):
        return self.balance >= self.bet

class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Blackjack Club')
        self.root.configure(bg='#061711')
        self.root.geometry('1280x820')
        self.root.minsize(1050, 700)
        self.root.bind('<Escape>', self.exit_fullscreen)

        self.players = [Player(i) for i in range(3)]
        self.player_count = 1
        self.active_indices = [0]
        self.current_player_pos = 0
        self.deck = []
        self.dealer_hand = []
        self.current_player_index = 0
        self.round_active = False

        self.build_ui()
        self.root.bind('<h>', lambda event: self.player_hit(self.current_player_index))
        self.root.bind('<H>', lambda event: self.player_hit(self.current_player_index))
        self.root.bind('<s>', lambda event: self.player_stand(self.current_player_index))
        self.root.bind('<S>', lambda event: self.player_stand(self.current_player_index))
        self.root.bind('<Return>', lambda event: self.start_round() if not self.round_active else None)
        self.update_player_panels()
        self.reset_table()

    def exit_fullscreen(self, event=None):
        del event
        self.root.attributes('-fullscreen', False)

    def build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#061711')
        style.configure('TLabel', background='#061711', foreground='#F7F3E8')
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('SubHeader.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('Small.TLabel', font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=(14, 8))
        style.map('TButton',
                  background=[('active', '#D8B45A'), ('disabled', '#31423B')],
                  foreground=[('disabled', '#9BA69F')])

        title_frame = tk.Frame(self.root, bg='#061711')
        title_frame.pack(fill='x', padx=24, pady=(16, 8))
        tk.Label(title_frame, text='BLACKJACK', bg='#061711', fg='#D8B45A',
                 font=('Segoe UI', 24, 'bold')).pack(side='left')
        tk.Label(title_frame, text='CLUB', bg='#061711', fg='#F7F3E8',
                 font=('Segoe UI', 24)).pack(side='left', padx=(8, 0))

        self.message_var = tk.StringVar(value='Wähle die Spieleranzahl und Einsätze.')
        message_frame = tk.Frame(title_frame, bg='#10251C', highlightthickness=1,
                                 highlightbackground='#315A48')
        message_frame.pack(side='right', fill='x', expand=True, padx=(40, 0), pady=4)
        tk.Label(message_frame, textvariable=self.message_var, bg='#10251C', fg='#F7F3E8',
                 font=('Segoe UI', 11), padx=16, pady=10).pack(fill='x')

        table = tk.Frame(self.root, bg='#0B422B', highlightthickness=2,
                         highlightbackground='#B99145')
        table.pack(fill='both', expand=True, padx=24, pady=10)

        dealer_area = tk.Frame(table, bg='#0B422B')
        dealer_area.pack(fill='x', padx=16, pady=(12, 4))
        tk.Label(dealer_area, text='DEALER', bg='#0B422B', fg='#D8B45A',
                 font=('Segoe UI', 11, 'bold')).pack()
        self.dealer_canvas = tk.Canvas(dealer_area, height=CARD_HEIGHT + 18,
                                       bg='#0B422B', highlightthickness=0)
        self.dealer_canvas.pack(fill='x')
        self.dealer_score_var = tk.StringVar(value='Noch keine Karten')
        tk.Label(dealer_area, textvariable=self.dealer_score_var, bg='#0B422B', fg='#F7F3E8',
                 font=('Segoe UI', 12, 'bold')).pack(pady=(2, 0))

        settings = tk.Frame(table, bg='#083720', highlightthickness=1,
                            highlightbackground='#4C735B')
        settings.pack(fill='x', padx=16, pady=(8, 10))

        tk.Label(settings, text='SPIELER', bg='#083720', fg='#D8CDAA',
                 font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, padx=(12, 4), pady=(8, 0), sticky='w')
        self.player_count_var = tk.IntVar(value=1)
        self.player_count_spin = tk.Spinbox(settings, from_=1, to=3, width=4,
                                             textvariable=self.player_count_var,
                                             command=self.change_player_count,
                                             state='readonly', font=('Segoe UI', 12, 'bold'),
                                             readonlybackground='#F7F3E8', justify='center')
        self.player_count_spin.grid(row=1, column=0, padx=12, pady=(2, 8), sticky='w')

        self.current_player_label = tk.Label(settings, text='Aktiver Spieler: Spieler 1',
                                             bg='#083720', fg='#F7F3E8',
                                             font=('Segoe UI', 12, 'bold'))
        self.current_player_label.grid(row=0, column=1, rowspan=2, padx=18, pady=8, sticky='w')

        controls_hint = tk.Label(settings, text='H / HIT     •     S / STAND     •     Enter / Runde',
                                 bg='#083720', fg='#AFC6B7', font=('Segoe UI', 9))
        controls_hint.grid(row=0, column=2, rowspan=2, padx=12, pady=8)

        self.new_round_button = ttk.Button(settings, text='Neue Runde starten',
                                           command=self.start_round)
        self.new_round_button.grid(row=0, column=3, rowspan=2, padx=12, pady=8, sticky='e')
        settings.columnconfigure(2, weight=1)

        self.players_frame = tk.Frame(table, bg='#0B422B')
        self.players_frame.pack(fill='both', expand=True, padx=8, pady=(2, 12))

        self.player_panels = []
        self.player_balance_vars = []
        self.player_bet_vars = []
        self.player_canvas = []
        self.player_status_vars = []
        self.player_bet_spins = []
        self.player_hit_buttons = []
        self.player_stand_buttons = []

        for index in range(3):
            panel = tk.Frame(self.players_frame, bg='#10251C', bd=1,
                             highlightthickness=2, highlightbackground='#315A48')
            panel.grid(row=0, column=index, sticky='nsew', padx=8, pady=4)
            self.players_frame.columnconfigure(index, weight=1, uniform='player')

            head = tk.Frame(panel, bg='#10251C')
            head.pack(fill='x', padx=12, pady=(10, 4))
            tk.Label(head, text=f'SPIELER {index + 1}', bg='#10251C', fg='#D8B45A',
                     font=('Segoe UI', 11, 'bold')).pack(side='left')

            balance_var = tk.StringVar(value=f'1.000 Chips')
            tk.Label(head, textvariable=balance_var, bg='#10251C', fg='#F7F3E8',
                     font=('Segoe UI', 11, 'bold')).pack(side='right')
            self.player_balance_vars.append(balance_var)

            bet_frame = tk.Frame(panel, bg='#10251C')
            bet_frame.pack(anchor='w', padx=12, pady=(4, 2))
            tk.Label(bet_frame, text='Einsatz', bg='#10251C', fg='#AFC6B7',
                     font=('Segoe UI', 9, 'bold')).pack(side='left')
            bet_var = tk.StringVar(value=str(BET_OPTIONS[0]))
            bet_spin = tk.Spinbox(bet_frame, values=BET_OPTIONS, width=7,
                                  textvariable=bet_var, font=('Segoe UI', 11, 'bold'),
                                  state='readonly', readonlybackground='#F7F3E8',
                                  justify='center',
                                  command=lambda idx=index: self.change_player_bet(idx))
            bet_spin.pack(side='left', padx=(8, 0))
            self.player_bet_vars.append(bet_var)
            self.player_bet_spins.append(bet_spin)

            canvas = tk.Canvas(panel, height=CARD_HEIGHT + 18, bg='#10251C', highlightthickness=0)
            canvas.pack(fill='x', padx=8, pady=6)
            self.player_canvas.append(canvas)

            status_var = tk.StringVar(value='Bereit')
            tk.Label(panel, textvariable=status_var, bg='#10251C', fg='#F7F3E8',
                     font=('Segoe UI', 12, 'bold')).pack(pady=(2, 6))
            self.player_status_vars.append(status_var)

            action_frame = tk.Frame(panel, bg='#10251C')
            action_frame.pack(pady=(0, 10))
            hit_button = ttk.Button(action_frame, text='Hit  (H)',
                                    command=lambda idx=index: self.player_hit(idx), state='disabled')
            hit_button.pack(side='left', padx=5)
            stand_button = ttk.Button(action_frame, text='Stand  (S)',
                                      command=lambda idx=index: self.player_stand(idx), state='disabled')
            stand_button.pack(side='left', padx=5)
            self.player_hit_buttons.append(hit_button)
            self.player_stand_buttons.append(stand_button)

            self.player_panels.append(panel)

    def change_player_count(self):
        self.player_count = self.player_count_var.get()
        self.active_indices = []
        for index, panel in enumerate(self.player_panels):
            if index < self.player_count:
                panel.grid()
                self.players[index].active = True
                self.active_indices.append(index)
            else:
                self.player_panels[index].grid_remove()
                self.players[index].active = False
        self.current_player_pos = 0
        self.current_player_index = self.active_indices[0] if self.active_indices else 0
        self.current_player_label.config(text=f'Aktiver Spieler: Spieler {self.current_player_index + 1}')
        self.update_player_panels()
        self.reset_table()

    def update_player_panels(self):
        for index, player in enumerate(self.players):
            self.player_balance_vars[index].set(f'{player.balance:,} Chips')
            self.player_bet_vars[index].set(str(player.bet))
            self.player_status_vars[index].set(player.status)
            if self.player_count > index:
                self.player_panels[index].grid()
            else:
                self.player_panels[index].grid_remove()

    def reset_table(self):
        for player in self.players:
            player.reset_hand()
        self.dealer_hand = []
        self.deck = []
        self.round_active = False
        self.current_player_pos = 0
        self.current_player_index = self.active_indices[0] if self.active_indices else 0
        self.update_player_panels()
        self.update_display()
        self.update_controls(False)
        self.current_player_label.config(text=f'Aktiver Spieler: Spieler {self.current_player_index + 1}')

    def change_player_bet(self, index):
        try:
            value = int(self.player_bet_vars[index].get())
        except ValueError:
            value = BET_OPTIONS[0]
        if value not in BET_OPTIONS:
            value = BET_OPTIONS[0]
        self.players[index].bet = value
        self.player_bet_vars[index].set(str(value))
        self.message_var.set(f'{self.players[index].name} setzt {value} Chips.')

    def create_deck(self):
        self.deck = [(rank, suit) for suit in SUITS for rank in RANKS]
        random.shuffle(self.deck)

    def draw_card(self):
        if not self.deck:
            self.create_deck()
        return self.deck.pop()

    def score_hand(self, hand):
        total = 0
        aces = 0
        for rank, _ in hand:
            if rank in ['J', 'Q', 'K']:
                total += 10
            elif rank == 'A':
                aces += 1
                total += 1
            else:
                total += int(rank)
        for _ in range(aces):
            if total + 10 <= 21:
                total += 10
        return total

    def start_round(self):
        if self.round_active:
            self.message_var.set('Die Runde läuft bereits.')
            return

        active_players = [self.players[i] for i in self.active_indices]
        if not active_players:
            self.message_var.set('Mindestens ein aktiver Spieler wird benötigt.')
            return

        for player in active_players:
            if player.bet > player.balance:
                self.message_var.set(f'{player.name} hat nicht genug Chips für den Einsatz.')
                return

        for player in active_players:
            player.reset_hand()
            player.balance -= player.bet

        self.create_deck()
        for player in active_players:
            player.hand = [self.draw_card(), self.draw_card()]
            player.blackjack = self.score_hand(player.hand) == 21
            player.status = 'Blackjack' if player.blackjack else 'Wartet'

        self.dealer_hand = [self.draw_card(), self.draw_card()]
        dealer_blackjack = self.score_hand(self.dealer_hand) == 21
        self.current_player_pos = 0
        self.current_player_index = -1
        self.round_active = True
        self.update_player_panels()
        self.update_display(hide_dealer=True)

        if dealer_blackjack:
            self.message_var.set('Dealer hat Blackjack! Runde wird ausgewertet.')
            self.dealer_play()
            self.finish_round()
            return

        self.message_var.set('Runde gestartet. Die Spieler sind der Reihe nach am Zug.')
        self.advance_to_next_player()

    def player_hit(self, index):
        if not self.round_active or index != self.current_player_index:
            return

        player = self.players[index]
        if player.status != 'Am Zug':
            return

        player.hand.append(self.draw_card())
        score = self.score_hand(player.hand)

        if score > 21:
            player.status = 'Bust'
            self.message_var.set(f'{player.name} hat sich überkauft ({score}).')
        elif score == 21:
            player.status = '21'
            self.message_var.set(f'{player.name} hat genau 21 und beendet den Zug.')
        else:
            self.message_var.set(f'{player.name} hat {score} Punkte.')

        self.update_player_panels()
        self.update_display(hide_dealer=True)
        if player.status in ['Bust', '21']:
            self.current_player_pos += 1
            self.advance_to_next_player()
        else:
            self.update_controls(True)

    def player_stand(self, index):
        if not self.round_active or index != self.current_player_index:
            return

        player = self.players[index]
        if player.status != 'Am Zug':
            return

        player.status = 'Stand'
        self.message_var.set(f'{player.name} steht mit {self.score_hand(player.hand)} Punkten.')
        self.update_player_panels()
        self.current_player_pos += 1
        self.advance_to_next_player()

    def advance_to_next_player(self):
        while self.current_player_pos < len(self.active_indices):
            index = self.active_indices[self.current_player_pos]
            player = self.players[index]

            if player.status == 'Wartet':
                player.status = 'Am Zug'
                self.current_player_index = index
                self.current_player_label.config(text=f'Aktiver Spieler: {player.name}')
                self.message_var.set(f'{player.name} ist am Zug.')
                self.update_player_panels()
                self.update_controls(True)
                self.highlight_current_player()
                return

            self.current_player_pos += 1

        self.current_player_index = -1
        self.current_player_label.config(text='Aktiver Spieler: -')
        self.update_controls(False)
        self.highlight_current_player()
        self.dealer_play()
        self.finish_round()

    def dealer_play(self):
        self.update_display(hide_dealer=False)
        while self.score_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.draw_card())
        dealer_score = self.score_hand(self.dealer_hand)
        if dealer_score > 21:
            self.message_var.set('Dealer hat sich überkauft!')
        else:
            self.message_var.set(f'Dealer steht mit {dealer_score}.')

    def finish_round(self):
        dealer_score = self.score_hand(self.dealer_hand)
        dealer_blackjack = dealer_score == 21 and len(self.dealer_hand) == 2

        for player in self.players[:self.player_count]:
            if player.status in ['Bereit', 'inaktiv']:
                continue
            player_score = self.score_hand(player.hand)
            result_text = ''
            payout = 0

            if player_score > 21:
                result_text = 'verloren (Bust)'
            elif dealer_blackjack:
                if player.blackjack:
                    payout = player.bet
                    result_text = 'Push (Blackjack)'
                else:
                    result_text = 'verloren (Dealer Blackjack)'
            elif player.blackjack:
                payout = int(player.bet * 2.5)
                result_text = 'Blackjack!'
            elif dealer_score > 21:
                payout = player.bet * 2
                result_text = 'Gewonnen (Dealer Bust)'
            elif player_score > dealer_score:
                payout = player.bet * 2
                result_text = 'Gewonnen'
            elif player_score == dealer_score:
                payout = player.bet
                result_text = 'Push'
            else:
                result_text = 'verloren'

            player.balance += payout
            player.status = f'{result_text} ({player_score})' if player_score <= 21 else result_text

        self.round_active = False
        self.update_player_panels()
        self.update_display(hide_dealer=False)
        self.update_controls(False)
        self.current_player_label.config(text='Aktiver Spieler: -')
        self.message_var.set('Runde beendet. Drücke Neue Runde starten für die nächste Runde.')

    def highlight_current_player(self):
        for index, panel in enumerate(self.player_panels):
            if index == self.current_player_index and self.round_active:
                panel.config(highlightbackground='#D8B45A', highlightthickness=3)
            elif index < self.player_count:
                panel.config(highlightbackground='#315A48', highlightthickness=2)
            else:
                panel.config(highlightbackground='#1A3227', highlightthickness=1)

    def all_players_done(self):
        for index in self.active_indices:
            if self.players[index].status == 'Am Zug':
                return False
        return True

    def draw_card_image(self, canvas, x, y, card, hidden=False):
        canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT,
                                fill='#173A57' if hidden else '#FFFDF8',
                                outline='#D8B45A' if hidden else '#1A1A1A', width=3)
        if hidden:
            canvas.create_oval(x + 24, y + 30, x + CARD_WIDTH - 24, y + CARD_HEIGHT - 30,
                               outline='#D8B45A', width=3)
            canvas.create_text(x + CARD_WIDTH / 2, y + CARD_HEIGHT / 2,
                               text='♠', fill='#D8B45A', font=('Segoe UI', 38, 'bold'))
            return

        rank, suit = card
        color = '#B91C1C' if suit in ['♥', '♦'] else '#171717'
        canvas.create_text(x + 12, y + 14, anchor='nw', text=rank,
                           fill=color, font=('Segoe UI', 16, 'bold'))
        canvas.create_text(x + CARD_WIDTH - 12, y + CARD_HEIGHT - 14, anchor='se', text=rank,
                           fill=color, font=('Segoe UI', 16, 'bold'))
        canvas.create_text(x + CARD_WIDTH / 2, y + CARD_HEIGHT / 2, text=suit,
                           fill=color, font=('Segoe UI', 44, 'bold'))

    def update_display(self, hide_dealer=False):
        self.dealer_canvas.delete('all')
        if self.dealer_hand:
            start_x = 20
            for index, card in enumerate(self.dealer_hand):
                hidden_card = hide_dealer and index == 1
                self.draw_card_image(self.dealer_canvas, start_x, 10, card, hidden=hidden_card)
                start_x += CARD_WIDTH + CARD_SPACING
            if hide_dealer:
                self.dealer_score_var.set('Dealer zeigt: ' + self.card_value_text(self.dealer_hand[0]))
            else:
                self.dealer_score_var.set('Dealer Punkte: ' + str(self.score_hand(self.dealer_hand)))
        else:
            self.dealer_score_var.set('Noch keine Karten')

        for index in range(3):
            canvas = self.player_canvas[index]
            canvas.delete('all')
            if index < self.player_count:
                player = self.players[index]
                start_x = max(12, (canvas.winfo_width() - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) // 2)
                for card in player.hand:
                    self.draw_card_image(canvas, start_x, 10, card)
                    start_x += CARD_WIDTH + CARD_SPACING
                if player.hand:
                    canvas.create_text(canvas.winfo_width() - 12, CARD_HEIGHT + 6,
                                       text=f'{self.score_hand(player.hand)} Punkte', anchor='e',
                                       fill='#D8B45A', font=('Segoe UI', 10, 'bold'))
            else:
                canvas.create_text(CARD_WIDTH, CARD_HEIGHT / 2, text='Inaktiv', fill='white', font=('Segoe UI', 20, 'bold'))

    def card_value_text(self, card):
        rank, _ = card
        return '10' if rank in ['J', 'Q', 'K'] else '11' if rank == 'A' else rank

    def update_controls(self, enabled):
        if enabled:
            self.new_round_button.state(['disabled'])
            self.player_count_spin.config(state='disabled')
            for index in range(3):
                if index == self.current_player_index and self.players[index].status == 'Am Zug':
                    self.player_hit_buttons[index].state(['!disabled'])
                    self.player_stand_buttons[index].state(['!disabled'])
                else:
                    self.player_hit_buttons[index].state(['disabled'])
                    self.player_stand_buttons[index].state(['disabled'])
                self.player_bet_vars[index].set(str(self.players[index].bet))
                if hasattr(self, 'player_bet_spins'):
                    self.player_bet_spins[index].config(state='disabled')
        else:
            self.new_round_button.state(['!disabled'])
            self.player_count_spin.config(state='readonly')
            if hasattr(self, 'player_bet_spins'):
                for bet_spin in self.player_bet_spins:
                    bet_spin.config(state='readonly')
