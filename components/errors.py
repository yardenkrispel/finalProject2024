class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def point_to_error(self):
        result = ''
        text = self.pos_start.txt
        start_idx = max(text.rfind('\n', 0, self.pos_start.idx), 0)
        end_idx = text.find('\n', start_idx + 1)
        if end_idx < 0:
            end_idx = len(text)

        for i in range(self.pos_end.ln - self.pos_start.ln + 1):
            line = text[start_idx:end_idx]
            start_col = self.pos_start.col if i == 0 else 0
            end_col = self.pos_end.col if i == self.pos_end.ln - self.pos_start.ln else len(line) - 1

            result += line + '\n' + (' ' * start_col + '^' * (end_col - start_col))

            start_idx = end_idx
            end_idx = text.find('\n', start_idx + 1)
            if end_idx < 0:
                end_idx = len(text)

        return result.replace('\t', '')

    def as_string(self):
        return f'{self.error_name}: {self.details}\n' + \
            f'Line {self.pos_start.ln + 1}\n\n' + \
            self.point_to_error()


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'IllegalCharacter', details)


class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'ExpectedCharacter', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'SyntaxError', details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'RuntimeError', details)
        self.context = context

    def as_string(self):
        traceback = self.generate_traceback()
        error_message = super().as_string()
        return traceback + error_message

    def generate_traceback(self):
        result, ctx = '', self.context
        while ctx:
            result = '\n' + result
            ctx = ctx.parent
        return 'Traceback (most recent call last):\n' + result


class TooManyVariablesError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'TooManyVariablesError', details)
        self.context = context


class TooManyNestedError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'TooManyNestedError', details)


class StackOverFlowError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'StackOverFlowError', details)
