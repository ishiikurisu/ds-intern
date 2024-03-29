import sys
import util
import collect_from_source as cfs

def get_output(config):
    return cfs.get_output(config).replace('.csv', '_balanced.csv')

def extract_balance(from_file):
    """
    Calculates the balance for each coordination in every year of the table.
    Returns a list of dicts, and each dict contains 4 keys:
    - The `source` coordination
    - The `target` coordination
    - The `year` that flow is referentiating
    - The personnel `flow` for that year between the coordinations
    This assumes the content from `from_file` is a CSV whose 1st and 2nd
    columns are ID and name, while the remaining columns are the relevant years.
    """
    outlet = []
    history = {}

    # Constructing history map
    with open(from_file, 'r', encoding='utf-8') as inlet:
        first_line = True
        years = []
        limit = -1
        for line in inlet:
            stuff = line.strip().split('\t')
            if first_line:
                years = [int(y) for y in stuff[2:]]
                limit = len(years)
                first_line = False
            else:
                # Incrementing history
                coords = stuff[2:]
                i = 1
                while i < limit:
                    target = coords[i].strip()
                    source = coords[i-1].strip()
                    year = years[i]
                    if target != source:
                        if source not in history:
                            history[source] = {}
                        if target not in history[source]:
                            history[source][target] = {}
                        if year not in history[source][target]:
                            history[source][target][year] = 0
                        history[source][target][year] += 1
                    i += 1

    # Turning history map into a list
    for source in history:
        for target in history[source]:
            for year in history[source][target]:
                flow = history[source][target][year]
                outlet.append({
                    'target': target,
                    'source': source,
                    'year': year,
                    'flow': flow,
                })

    return outlet

def save_balance(balance, to_file):
    with open(to_file, 'w', encoding='utf-8') as outlet:
        outlet.write('source\ttarget\tyear\tflow\n')
        for entry in balance:
            line = '{0}\t{1}\t{2}\t{3}\n'.format(entry['source'],
                                                 entry['target'],
                                                 entry['year'],
                                                 entry['flow'])
            outlet.write(line)

if __name__ == '__main__':
    config = util.load_config(sys.argv[1])
    from_file = cfs.get_output(config)
    to_file = get_output(config)
    balance = extract_balance(from_file)
    save_balance(balance, to_file)
