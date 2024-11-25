def generate_parts(start, end, parts):
    # Calculate the number of IDs in each part
    ids_per_part = (end - start + 1) // parts
    remainder = (end - start + 1) % parts

    part_start = start
    for i in range(parts):
        part_end = part_start + ids_per_part - 1 + (1 if i < remainder else 0)
        yield part_start, part_end
        part_start = part_end + 1


if __name__ == '__main__':
    parts = 30
    spider = 'swg'
    start = 9500
    end = 15000
    conc_req = 8

    for part_number, (part_start, part_end) in enumerate(generate_parts(start, end, parts), 1):
        print(f'''start "{spider}_start_{part_start}_end_{part_end}"
                scrapy crawl {spider} 
                -a start_id={part_start} 
                -a end_id={part_end} 
                -s CONCURRENT_REQUESTS={conc_req}''')
