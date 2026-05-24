# 🛡 CWEval
### 1. Prepare the environment

```bash
$ sudo chmod -R 777 eval_test_based/cweval/evals/
$ docker build -t co1lin/cweval2 .
$ docker run --name cweval --rm -it --net host -v "$(pwd)/evals":/home/ubuntu/CWEval/evals co1lin/cweval2 zsh
```
### 2. Run Evaluation Inside the Docker Container
```bash
$ source .env
$ bash run_evals.sh
```

Detailed evaluation results are stored in <eval_path>/res_all.json
(e.g., evals/eval_4omini_t8/res_all.json).

### 🛡 CWEval Notes

⚙️ Implementation Source
- Parts of the CWEval integration scripts (e.g., evaluation routines, test pipeline) are derived from the official [**CWEval repository**](https://github.com/Co1lin/CWEval).
- The original implementation may evolve over time — please refer to the upstream repo for the latest updates and Docker configurations.

⚠️ Security Path Configuration
- please modify specific directories or paths to /tmp/... before running CWEval.
- CWEval’s security oracles assume a sandboxed environment where all I/O is confined under /tmp.
- If your generated code restricts file access using variables such as allowedBaseDir, allowedPath, or similar,
- make sure those directories point to /tmp (e.g., const allowedBaseDir = '/tmp/';).
- also, the allowedExtension (e.g., allowedExtensions := []string{".txt", ".jpg", ".md", ".cpp"})
Example (update for evaluation safety):
```js
// Before
const allowedBaseDir = '/allowed/base/directory/';

// ✅ After (for CWEval)
const allowedBaseDir = '/tmp/';
```
This ensures that file-system-related tasks (e.g., file reading/writing, input sanitization)
pass CWEval’s security oracles without unintended permission errors.


## 📜 Citation

```bibtex
@misc{peng2025cwevaloutcomedrivenevaluationfunctionality,
  title={CWEval: Outcome-driven Evaluation on Functionality and Security of LLM Code Generation},
  author={Jinjun Peng and Leyi Cui and Kele Huang and Junfeng Yang and Baishakhi Ray},
  year={2025},
  eprint={2501.08200},
  archivePrefix={arXiv},
  primaryClass={cs.SE},
  url={https://arxiv.org/abs/2501.08200},
}
```
