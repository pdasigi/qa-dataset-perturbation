import json
import sys
import hashlib
from collections import defaultdict

output_file = sys.argv[1]
all_data = defaultdict(lambda: defaultdict(lambda: {'qas': []}))  # {(title, url) -> {context_id -> {}}}
for filename in sys.argv[2:]:
    file_data = json.load(open(filename))["data"]
    for article_info in file_data:
        title = article_info["title"]
        url = article_info["url"]
        for paragraph_info in article_info["paragraphs"]:
            context_id = paragraph_info['context_id']
            context = paragraph_info['context']
            paragraph_has_perturbations = False
            perturbed_qa_info = []
            for qa_info in paragraph_info["qas"]:
                if "original_id" in qa_info:
                    paragraph_has_perturbations = True
                elif "_" in qa_info['id']:
                    # This was Dheeru's perturbation. The original id is the string before the underscore.
                    qa_info["original_id"] = qa_info['id'].split('_')[0]
                    paragraph_has_perturbations = True
                else:
                    continue
                # Some of the perturbations were done manually. So recomputing id just to be sure.
                updated_id = hashlib.sha1(f"{paragraph_info['context_id']} {qa_info['question']}".encode()).hexdigest()
                # Also recomputing answer starts
                for answer_info in qa_info['answers']:
                    try:
                        answer_info['answer_start'] = context.index(answer_info['text'])
                    except ValueError as error:
                        print("Could not find answer!")
                        print(f"Context was {context}")
                        print(f"Answer was {answer_info['text']}")
                        raise error
                qa_info['id'] = updated_id
                perturbed_qa_info.append(qa_info)

            if paragraph_has_perturbations:
                perturbed_paragraph_info = all_data[(title, url)][context_id]
                perturbed_paragraph_info['context'] = context
                perturbed_paragraph_info['context_id'] = context_id
                for qa_info in perturbed_qa_info:
                    perturbed_paragraph_info['qas'].append(qa_info)

perturbed_data = {"data": []}
for (title, url), paragraphs_info in all_data.items():
    article_info = {"title": title,
                    "url": url,
                    "paragraphs": list(paragraphs_info.values())}
    perturbed_data['data'].append(article_info)

with open(output_file, "w") as out_ptr:
    json.dump(perturbed_data, out_ptr, indent=2)
