import ulid


def generate_ulid():
  return str(ulid.new())
