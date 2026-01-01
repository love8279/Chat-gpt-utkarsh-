def extract_course_to_file(batch_id):
    # yahan tumhara REAL extraction logic hoga

    links = [
        ("Video 1", "url1"),
        ("Video 2", "url2"),
    ]

    filename = f"course_{batch_id}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for title, url in links:
            f.write(f"{title}: {url}\n")

    return filename
    
