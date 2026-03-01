# Data Documentation

This directory contains the datasets used for fine-tuning the model to simulate kin/family relationships.

## File Descriptions

### Source Data
* **`kin_dial_ultra_quality.jsonl`**: The primary high-quality dataset. It contains multi-turn conversations designed to simulate a caring family member (e.g., parent, grandparent).
    * **Format**: Chat completion format (`messages` list).
    * **Features**:
        * **System Prompt**: Specifies the user's context (e.g., `Context: User is a CHILD.`).
        * **User Inputs**: Prefixed with age/role tags like `[CHILD]`, `[YOUNG_ADULT]`.
        * **Assistant Outputs**: Empathetic, warm, and role-appropriate responses.

### Training Splits
* **`train_kin.jsonl`**: The training subset of the data. Used for the actual fine-tuning process.
* **`eval_kin.jsonl`**: The evaluation/validation subset. Used to monitor loss and metrics during training to prevent overfitting.

### Preprocessed files
* **`formatted_train.jsonl`**: The `train_kin.jsonl` data processed and formatted specifically for the fine-tuning script (e.g., Mistral/Llama formatted).
* **`formatted_val.jsonl`**: The `eval_kin.jsonl` data processed and formatted for validation during fine-tuning.
* **`temp_formatted_data.jsonl`**: A temporary file generated during the data formatting pipeline. Can usually be ignored or deleted.

## Data Format Example

Each line in the `.jsonl` files is a JSON object with a `messages` key:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Context: User is a CHILD."
    },
    {
      "role": "user",
      "content": "[CHILD] How about going to dance this evening?"
    },
    {
      "role": "assistant",
      "content": "\"Great idea! There’s a fun place nearby where people dance and have a good time—do you know it?\""
    }
  ]
}
```
