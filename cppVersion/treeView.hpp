#ifndef TREEVIEW_H_
#define TREEVIEW_H_

#include <string>
#include <list>
#include <vector>
#include <algorithm>

// ROOT
// ╠<aaa>
// ║╠<aaa>
// ║║╚<aaa>
// ║╚<aaa>
// ╚<aaa>
//
//╣
//║
//╗
//╝
//╚
//╔
//╩
//╦
//╠
//═
//╬

#define V_ "\e[32m║\e[0m"
#define TR_ "\e[32m╚\e[0m"
#define TRB_ "\e[32m╠\e[0m"

template <typename T>
std::string TreeView(std::string (*text)(const T&) , std::list<T> (*childrenNodes)(const T&), const T& tree, bool last = false) {
    static int depth = -1;
    static std::vector<int> donedepths = {};
    std::string res = "";
    res += "\e[36m<\e[0m" + text(tree) + "\e[36m>\e[0m\n";
    if (last) donedepths.push_back(depth);
    depth++;
    auto children = childrenNodes(tree);
    size_t n = 0;
    for (auto const& c : children)
    {
        for (int i = 0; i < depth; i++) if (std::find_if(donedepths.begin(), donedepths.end(), [i](int n){return i == n;})!=donedepths.end()) res += " "; else res += V_;
        if (children.size()-1 == n) res += TR_;
        else res += TRB_;
        res += TreeView(text, childrenNodes, c, children.size()-1 == n);
        n++;
    }
    depth--;
    if (last) donedepths.pop_back();
    return res;
}

#undef V_
#undef TR_
#undef TRB_

#endif // TREEVIEW_H_
