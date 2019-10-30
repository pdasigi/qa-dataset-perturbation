import re
import sys
import json
import random
import hashlib
import datetime

def get_answers(context):
    print("Enter answer spans below. You can copy text from the context and paste here.")
    print("Hit enter if you are done inputting all answer spans")
    new_answers = []
    current_span = None
    span_index = 0
    while current_span != '':
        current_span = input(f"Span {span_index + 1}: ")
        if current_span != '':
            # Important note: This will only find the first index of the answer.
            try:
                answer_start = context.index(current_span)
                new_answers.append({"text": current_span,
                                    "answer_start": answer_start})
            except ValueError:
                print("Could not find answer span in the context! Please try again.")
                continue
        span_index += 1
    return new_answers


def get_new_passage(context):
    while True:
        string_to_replace = input("Enter a unique string from the passage that you want to change: ")
        num_occurrences = len(re.findall(string_to_replace, context))
        if num_occurrences == 0:
            print("The string you entered does not occur in the passage. Please try again!")
        elif num_occurrences > 1:
            print("The string you entered is not unique. Please try again!")
        else:
            replacement = input("Enter a replacement: ")
            new_context = context.replace(string_to_replace, replacement)
            return new_context


def add_perturbations(data):
    data_indices = list(range(len(data["data"])))
    random.shuffle(data_indices)
    for datum_index in data_indices:
        datum = data["data"][datum_index]
        for paragraph_info in datum["paragraphs"]:
            question_ids = {qa_info["id"] for qa_info in paragraph_info["qas"]}
            print("\nContext:")
            context = paragraph_info["context"]
            context_id = paragraph_info["context_id"]
            print(context)
            qa_indices = list(range(len(paragraph_info["qas"])))
            random.shuffle(qa_indices)
            for qa_index in qa_indices:
                qa_info = paragraph_info["qas"][qa_index]
                if "original_id" in qa_info:
                    # This is a perturbed instance. Let's not perturb it further.
                    continue
                original_id = qa_info["id"]
                question = qa_info['question']
                print(f"\nQuestion: {question}")
                print(f"Answers: {[a['text'] for a in qa_info['answers']]}")
                print("You can modify the question or the passage, skip to the next question, or exit.")
                response = input("Type a new question, hit enter to skip, type 'p' to edit passsage or 'exit' to end session: ")
                if len(response) > 1 and response.lower() != 'exit':
                    perturbed_question = response.strip()
                    new_id = hashlib.sha1(f"{context} {perturbed_question}".encode()).hexdigest()
                    if new_id not in question_ids:
                        new_answers = get_answers(context)
                        if new_answers:
                            new_qa_info = {"question": perturbed_question,
                                           "id": new_id,
                                           "answers": new_answers,
                                           "original_id": original_id}
                        paragraph_info["qas"].append(new_qa_info)
                    else:
                        print("This question exists in the dataset! Please try again.\n")
                elif response.lower() == 'exit':
                    print("Ending session. Thank you!")
                    return
                elif response.lower() == "p":
                    perturbed_context = get_new_passage(context)
                    new_context_id = hashlib.sha1(perturbed_context.encode()).hexdigest()
                    print(f"New context: {perturbed_context}\n")
                    new_id = hashlib.sha1(f"{perturbed_context} {question}".encode()).hexdigest()
                    new_answers = get_answers(perturbed_context)
                    if new_answers:
                        new_qa_info = {"question": question,
                                       "id": new_id,
                                       "answers": new_answers,
                                       "original_id": original_id}
                    new_paragraph_info = {"context": perturbed_context,
                                          "qas": [new_qa_info],
                                          "context_id": new_context_id,
                                          "original_context_id": context_id}
                    datum["paragraphs"].append(new_paragraph_info)


def main():
    if len(sys.argv) == 2:
        input_filename = sys.argv[1]
        data = json.load(open(input_filename))
        add_perturbations(data)
        filename_prefix = input_filename.split("/")[-1].split(".")[0]
        # Removing previous timestamp if any
        filename_prefix = re.sub('_2019[0-9]*$', '', filename_prefix)
        output_name_suffix = ''
        if '_perturbed' not in filename_prefix:
            output_name_suffix = '_perturbed'
        timestamp = re.sub('[^0-9]', '', str(datetime.datetime.now()).split('.')[0])
        # Will be written in current directory
        output_filename = f"{filename_prefix}{output_name_suffix}_{timestamp}.json"
        json.dump(data, open(output_filename, "w"), indent=2)
    else:
        print(f"Usage: python {sys.argv[0]} /path/to/data.json")
        print('''Pro-tip: If you previously used this interface, provide the output from that session as the input
              here. The resulting dataset from this session will contain a union of your perturbations from both
              sessions.''')


if __name__ == '__main__':
    main()
