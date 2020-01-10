#include "binheap.hpp"

#include <cstddef>
#include <string>

template<class T>
class APQPayload {
public:
	std::size_t index;
	std::string key;
	T data;

	void setIndex(std::size_t index) {
		this->index = index;
	}
};

template<class T>
class DefaultSetIndex<APQPayload<T>*> {
public:
	void operator()(APQPayload<T>* el, std::size_t index) const {
		el->setIndex(index);
	}
};
