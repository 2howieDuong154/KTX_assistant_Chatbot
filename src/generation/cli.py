from src.generation.pipeline import ask

def main():
    print("Chatbot KTX Đại Học Cần Thơ (Enter trống để thoát)")
    while True:
        q = input("\nHỏi: ").strip()
        if not q:
            break
        r = ask(q)
        print("\n" + r["answer"])
        for s in r["sources"]:
            print(f"  [{s['id']}] {s['title']} | {s['section']} | "
                  f"trang {s['page']} | |")

if __name__ == "__main__":
    main()