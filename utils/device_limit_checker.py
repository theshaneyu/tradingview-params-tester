from .email_sender import send_email


class DeviceLimitChecker:
    def __init__(self) -> None:
        self.last_profit_and_win_rate = ''
        self.duplication_counter = 0
        self.warning_email_sent = False

    def check(self, profit_and_win_rate_str: str) -> None:
        if self.warning_email_sent:
            return

        if profit_and_win_rate_str == self.last_profit_and_win_rate:
            self.duplication_counter += 1

            if self.duplication_counter > 30:
                # get the same profit and win rate continuously
                send_email('可能發生超過裝置上限', '可能發生超過裝置上限')
                self.warning_email_sent = True

        else:
            self.last_profit_and_win_rate = profit_and_win_rate_str
            self.duplication_counter = 0
