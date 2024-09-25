from Node_f1_score_v2 import calculate_metrics as node_metrics
from Edge_f1_score_v2 import calculate_metrics as edge_metrics
from f1_score_funcs import get_avg_f1_score

pred_dir_name = "../datasets/predicted_annotations"
ref_dir_name = "../datasets/Synthetic_v2/JSON"
print("AVERAGE NODE SCORE", str(get_avg_f1_score(node_metrics, pred_dir_name, ref_dir_name)))
print("AVERAGE EDGE SCORE", str(get_avg_f1_score(edge_metrics, pred_dir_name, ref_dir_name)))