
if __name__ == "__main__":
    keys = sys.argv[1:] or list(D)
    for k in keys:
        run(k, D[k])
