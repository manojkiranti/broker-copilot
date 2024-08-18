def split_name(full_name):
    parts = full_name.split()
    if len(parts) >= 2:
        return parts[0], ' '.join(parts[1:])
    elif parts:
        return parts[0], ""  
    return "", ""