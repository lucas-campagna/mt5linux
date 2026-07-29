FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY mt5linux ./mt5linux
COPY README.md ./

RUN pip install --no-cache-dir build && \
    python -m build && \
    pip install --no-cache-dir dist/*.whl

RUN python -c "import mt5linux; import numpy; import plumbum; import pyparsing; import rpyc; print('All dependencies imported successfully!')"

CMD ["python", "-c", "from mt5linux import MetaTrader5; print('mt5linux ready')"]
