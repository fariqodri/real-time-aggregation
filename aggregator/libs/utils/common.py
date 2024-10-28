def parse_conf(conf):
    """
    Parse configuration string in the format key1=value1,key2=value2,...
    """
    return dict(map(lambda s: s.split('='), conf))