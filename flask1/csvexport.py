import io
import datetime
from flask import send_file

class CsvExporter:
    _nl = '\n'.encode('utf-8')

    def __init__(self, filename):
        self.buffer = io.BytesIO()
        self.fname = filename

        # explicitar separador para el windows excel
        self.buffer.write('sep=,'.encode('utf-8') + self._nl)

    def writeHeaders(self,str):
        self.buffer.write(str.encode('utf-8') + self._nl)

    def writeVals(self, vals):
        for i,v in enumerate(vals):
            if not isinstance(v, str):
                if isinstance(v, datetime.date):
                    vals[i]=v.strftime("%d/%m/%Y %H:%M")
                else:
                    vals[i]=str(v)
            elif v.find(',') >= 0 and v[0]!='"':
                vals[i]='"{}"'.format(v)
        self.buffer.write(','.join(vals).encode('utf-8') + self._nl)

    def send(self):
        self.buffer.seek(0)
        return send_file(self.buffer, add_etags=False, cache_timeout=0, attachment_filename=self.fname, as_attachment=True)
        #return send_file(self.buffer, attachment_filename=self.fname, as_attachment=True)