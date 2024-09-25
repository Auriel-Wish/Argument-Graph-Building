import json
import re
import glob

def fetch_span_list(file_path):
    pattern = re.compile(r'\b\w+\b')
    with open(file_path, 'r') as file:
        data = json.loads(file.read())
        all_spans = []
        for node in data["nodes"]:
            text = node["text"]
            words = pattern.findall(text)
            all_spans.append(words)
    return all_spans

def get_spans():
    reference_list = []
    prediction_list = []

    # Change this depending on which model's predictions you want to check
    pred_dir_name = "Datasets/Zero-Shot-Predicted-JSON"
    ref_dir_name = "Datasets/Synthetic/Reference-JSON"
    
    prediction_dir = glob.glob(pred_dir_name + "/*")
    reference_dir = glob.glob(ref_dir_name + "/*")

    for dir in prediction_dir:
        for dir2 in reference_dir:
            if (dir.split("/")[-1] == dir2.split("/")[-1]):
                pred_dataset_dir = glob.glob(dir + "/*")
                for path in pred_dataset_dir:
                    print(path)
                    curr_ref_fname = ref_dir_name + "/" + path.split("/")[-2] + "/" + path.split("/")[-1]
                    reference_list.append(fetch_span_list(curr_ref_fname))
                    prediction_list.append(fetch_span_list(path))
            #break # REMOVE LATER
    
    return {"reference_list":reference_list, "prediction_list":prediction_list}

# span1 = reference
# span2 = predicted
def calculate_metrics(predicted_spans, reference_spans, match_type='exact', iou_threshold=0.5):
    def exact_match(span1, span2):
        return span1 == span2

    def partial_match(span1, span2):
        count = len(set(span1) & set(span2))
        if(count > 0.5 * len(span1)):
            return True
        return False

    def iou(span1, span2):
        set1, set2 = set(span1), set(span2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union != 0 else 0

    match_function = {
        'exact': exact_match,
        'partial': partial_match,
        'iou': lambda s1, s2: iou(s1, s2) >= iou_threshold
    }.get(match_type, exact_match)

    predicted_spans_set = [tuple(span) for span in predicted_spans]
    reference_spans_set = [tuple(span) for span in reference_spans]

    true_positives = 0
    for pred_span in predicted_spans_set:
        for ref_span in reference_spans_set:
            if match_function(pred_span, ref_span):
                true_positives += 1

    false_positives = len(predicted_spans_set) - true_positives
    false_negatives = len(reference_spans_set) - true_positives

    precision = float('%.3f'%(true_positives / (true_positives + false_positives) if predicted_spans_set else 0))
    recall = float('%.3f'%(true_positives / (true_positives + false_negatives) if reference_spans_set else 0))
    f1_score = float('%.3f'%(2 * precision * recall / (precision + recall) if precision + recall > 0 else 0))

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

# Example usage
# predicted_spans = [['token1', 'token2'], ['token3', 'token4']]
# reference_spans = [['token1', 'token2'], ['token5', 'token6']]

all_spans = get_spans()

# Calculate exact match metrics
# exact_metrics = calculate_metrics(all_spans["prediction_list"][0], all_spans["reference_list"][0], match_type='exact')
# print('Exact Match Metrics:', exact_metrics)

# partial_match_metrics = calculate_metrics(all_spans["prediction_list"][0], all_spans["reference_list"][0], match_type='partial')
# print('Partial Match Metrics:', partial_match_metrics)




averages = {"precision":0, "recall":0, "f1_score":0}

for i in range(len(all_spans["prediction_list"])):
    IoU_match_metrics = calculate_metrics(all_spans["prediction_list"][i], all_spans["reference_list"][i], match_type='iou', iou_threshold=0.5)
    averages["precision"] += IoU_match_metrics["precision"]
    averages["recall"] += IoU_match_metrics["recall"]
    averages["f1_score"] += IoU_match_metrics["f1_score"]

    print(IoU_match_metrics)

averages["precision"] = float('%.3f'%(averages["precision"] / len(all_spans["prediction_list"])))
averages["recall"] = float('%.3f'%(averages["recall"] / len(all_spans["prediction_list"])))
averages["f1_score"] = float('%.3f'%(averages["f1_score"] / len(all_spans["prediction_list"])))

print("IoU averages: " + str(averages))




    
# IoU_match_metrics = calculate_metrics(all_spans["prediction_list"][0], all_spans["reference_list"][0], match_type='iou', iou_threshold=0.5)
# print('IoU Match Metrics:', IoU_match_metrics)

# Calculate partial match metrics
# partial_match_metrics = calculate_metrics(predicted_spans, reference_spans, match_type='partial')
# print('IoU Metrics:', partial_match_metrics)

# Calculate IoU match metrics
# iou_metrics = calculate_metrics(predicted_spans, reference_spans, match_type='iou', iou_threshold=0.5)
# print('IoU Metrics:', iou_metrics)