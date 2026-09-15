import subprocess

def run_all():
    print("Running Assembler...")

    # chạy assembler
    result1 = subprocess.run(
        ["python", "assembler.py", "program.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(result1.stdout)

    if result1.returncode != 0:
        print("Assembler error:")
        print(result1.stderr)
        return

    print("Running ISS...")

    # chạy ISS
    result2 = subprocess.run(
        ["python", "ISS.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(result2.stdout)

    if result2.returncode != 0:
        print("ISS error:")
        print(result2.stderr)
        return

    print("Done")

if __name__ == "__main__":
    run_all()