template<typename... ARGS> struct slice;

// if we had access to C++17, we could just make these a tuple of optionals, but were not to be

template<typename S_TYPE, typename E_TYPE, typename T_TYPE>
struct slice<S_TYPE, E_TYPE, T_TYPE>{
    S_TYPE start;
    bool has_start;
    E_TYPE end;
    bool has_end;
    T_TYPE step;
    bool has_step;
};

template<typename S_TYPE, typename E_TYPE>
struct slice<S_TYPE, E_TYPE>{
    S_TYPE start;
    bool has_start;
    E_TYPE end;
    bool has_end;
};
