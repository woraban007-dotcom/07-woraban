import sys
import subprocess
import re
import os

def extract_numbers(text):
    """ดึงตัวเลขทั้งหมดออกจาก Output ของนักเรียน"""
    return [float(n) if '.' in n else int(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]

def has_student_code(file_path):
    """ตรวจสอบว่านักเรียนได้เขียนโค้ดตอบหรือไม่ (ไม่นับบรรทัดว่างและ Comment)"""
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        code_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
        return len(code_lines) > 0
    except Exception:
        return False

def run_test(file_path, input_data):
    """สั่งรันไฟล์ Python ของนักเรียนพร้อมป้อนค่า Input"""
    try:
        proc = subprocess.run(
            [sys.executable, file_path],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=3
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout Error (โปรแกรมทำงานค้าง/Infinite Loop)", -1
    except Exception as e:
        return "", str(e), -1

TEST_CASES = {
    "Examination_1.py": [
        {"input": "100\n10\n", "expected": 800},
        {"input": "100\n6\n", "expected": 540},
        {"input": "100\n3\n", "expected": 300}
    ],
    "Examination_2.py": [
        {"input": "85\n", "expected": 4},
        {"input": "65\n", "expected": 2},
        {"input": "45\n", "expected": 0}
    ],
    "Examination_3.py": [
        {"input": "15\n42\n8\n", "expected": 42},
        {"input": "100\n50\n75\n", "expected": 100},
        {"input": "-5\n-1\n-10\n", "expected": -1}
    ],
    "Examination_4.py": [
        {"input": "30\n", "expected": 90},
        {"input": "70\n", "expected": 250}
    ],
    "Examination_5.py": [
        {"input": "5\n5\n5\n", "expected": "สามเหลี่ยมด้านเท่า"},
        {"input": "5\n5\n3\n", "expected": "สามเหลี่ยมหน้าจั่ว"},
        {"input": "3\n4\n5\n", "expected": "สามเหลี่ยมด้านไม่เท่า"}
    ]
}

def grade_problem(file_name, cases):
    if not os.path.exists(file_name):
        return 0.0, "❌ ไม่พบไฟล์"
    
    if not has_student_code(file_name):
        return 0.0, "⚪ ยังไม่ได้เริ่มทำ"

    total_score = 0.0
    max_score = 4.0
    score_per_case = max_score / len(cases)
    has_execution_error = False
    passed_cases = 0

    for case in cases:
        out, err, returncode = run_test(file_name, case["input"])
        
        if returncode != 0:
            has_execution_error = True
            continue

        expected = case["expected"]

        # 1. ตรวจกรณีผลลัพธ์เป็นข้อความ (String)
        if isinstance(expected, str):
            clean_out = re.sub(r'\s+', '', out)
            clean_expected = re.sub(r'\s+', '', expected)
            if clean_expected in clean_out:
                passed_cases += 1
                total_score += score_per_case
        # 2. ตรวจกรณีผลลัพธ์เป็นตัวเลข (Number)
        else:
            nums = extract_numbers(out)
            if expected in nums or any(abs(n - expected) < 0.01 for n in nums):
                passed_cases += 1
                total_score += score_per_case

    # คะแนนพยายาม (Effort Score) 1.00/4.00 คะแนน
    if total_score == 0.0 and has_student_code(file_name):
        total_score = 1.00
        if has_execution_error:
            status_msg = "⚠️ โค้ดมีข้อผิดพลาด (Syntax/Runtime Error) - ได้คะแนนพยายาม 1.00/4.00"
        else:
            status_msg = "❌ คำตอบยังไม่ถูกต้อง - ได้คะแนนพยายาม 1.00/4.00"
    else:
        status_msg = f"✅ ผ่าน {passed_cases}/{len(cases)} เคส ({total_score:.2f}/4.00)"

    return round(total_score, 2), status_msg

if __name__ == "__main__":
    print("==========================================")
    print("   สรุปผลการตรวจคะแนนข้อสอบ (รวม 20 คะแนน)")
    print("==========================================")
    
    total = 0.0
    for i in range(1, 6):
        file_name = f"Examination_{i}.py"
        score, status = grade_problem(file_name, TEST_CASES[file_name])
        print(f"ข้อที่ {i} ({file_name}): {score:.2f} / 4.00 คะแนน | {status}")
        total += score
        
    print("------------------------------------------")
    print(f"คะแนนรวมทั้งหมด: {total:.2f} / 20.00 คะแนน")
    print("==========================================")
