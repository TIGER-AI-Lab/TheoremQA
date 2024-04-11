from examples import examples
from data_loader import get_prompt
from openai import OpenAI
import data_loader
import argparse
import json
import utils
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--model", default='', type=str)
parser.add_argument("--form", default='short', type=str)
args = parser.parse_args()

client = OpenAI()

def run_question_answer(questions: list, groundtruths: list):
    system_prompt = """You are a science teacher, you are supposed to provide a solution to a given problem. You need to output the answer in your final sentence like "Therefore, the answer is ...". The answer can only be one of the following forms:
1. a numerical value like 0.1, no symbol at all.
2. a list of number like [2, 3, 4].
3. True/False.
4. an option like (a), (b), (c), (d)
"""

    results = []
    for question, groundtruth in tqdm(zip(questions, groundtruths)):
        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": 'Problem:' + question + '\nSolution:'
                }
            ],
            temperature=0.1,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        tmp = response.choices[0].message.content
        if len(tmp.split('answer is ')) == 2:
            output, answer = tmp.split('answer is ')
        else:
            print(tmp)
            output, answer = tmp, ''

        results.append((question, output.strip(), answer.strip(), groundtruth))
    return results


if __name__ == "__main__":
    questions, groundtruths = data_loader.load_dataset()

    returned_values = run_question_answer(questions, groundtruths)

    if not args.output:
        filename = 'gpt_4_turbo'
        filename += '_' + f'{args.shots}shots' + '_' + args.form
        args.output = f'outputs/{filename}.jsonl'
        print('Writing the output to', args.output)

    file_handle = open(args.output, 'w')

    correct, wrong = 0, 0
    for question, output, answer, groundtruth in returned_values:
        if isinstance(groundtruth, str):
            groundtruth = [groundtruth]
        if utils.compare_answer_with_groundtruth(answer, *groundtruth):
            correct += 1
        else:
            wrong += 1

        # print(answer, '#', groundtruth, '#', correct / (correct + wrong))

        example = {
            'question': question,
            'correct': groundtruth,
            'solution': output,
            'pred': answer,
        }

        file_handle.write(json.dumps(example) + '\n')

    print('Final Accuracy: ', correct / (correct + wrong))
    print('finished one epoch')

    file_handle = open(args.output, 'w')

    correct, wrong = 0, 0
    for question, output, answer, groundtruth in returned_values:
        if isinstance(groundtruth, str):
            groundtruth = [groundtruth]
        if utils.compare_answer_with_groundtruth(answer, *groundtruth):
            correct += 1
        else:
            wrong += 1

        # print(answer, '#', groundtruth, '#', correct / (correct + wrong))

        example = {
            'question': question,
            'correct': groundtruth,
            'solution': output,
            'pred': answer,
        }

        file_handle.write(json.dumps(example) + '\n')

    print('Final Accuracy: ', correct / (correct + wrong))
    print('finished one epoch')