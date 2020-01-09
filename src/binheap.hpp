#ifndef BIN_HEAP_H
#define BIN_HEAP_H

#include <algorithm>
#include <cstddef>
#include <vector>
#include <functional>

template<
	class T = void
>
class DefaultSetIndex {
public:
	void operator()(T& el, std::size_t index) const {}
};

template<
	class T,
	class Container = std::vector<T>,
	class Compare = std::less<typename Container::value_type>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
class BinHeap {
public:
	using container_type = Container;
	using value_compare = Compare;
	using value_set_index = SetIndex;

	using value_type = typename Container::value_type;
	using size_type = typename Container::size_type;
	using difference_type = typename Container::difference_type;
	using reference = typename Container::reference;
	using const_reference = typename Container::const_reference;

	using iterator = typename Container::iterator;
	using const_iterator = typename Container::const_iterator;

protected:
	Container container;
	Compare compare;
	SetIndex setIndex;

	void siftUp(size_type holeInd, size_type startInd, value_type&& value) {
		/*
		 * container is a heap at all indices >= startInd, except possibly
		 * for holeInd. startInd < holeInd or no work is done. value is
		 * presumed at holeInd and must be less than any of the holeInd
		 * children (simple case: leaf).
		 *
		 * Restore the heap invariant by moving value to the right position by
		 * moving up the hole until parent is <= value.
		 */

		while (holeInd > startInd) {
			const size_type parentPos = (holeInd - 1) / 2;
			if (!compare(value, container[parentPos]))
				// parent <= value
				break;

			container[holeInd] = std::move(container[parentPos]);
			setIndex(container[holeInd], holeInd);
			holeInd = parentPos;
		}

		container[holeInd] = std::move(value);
		setIndex(container[holeInd], holeInd);
	}

	void siftDown(size_type holeInd, value_type&& value) {
		/*
		 * container is a heap at all indices of the sub-tree (transitive
		 * children) of holeInd except possibly at holeInd. value is presumed
		 * at holeInd.
		 *
		 * Restore the heap invariant by moving down the hole by bubbling up
		 * the smaller child starting at holeInd (recursively until reaching a
		 * leaf), then using siftUp to move value to the right place.
		 */

		const size_type len = container.size();
		const size_type limit = (len - 1) / 2; // first index that does not have two children
		const size_type startInd = holeInd;

		// while the hole has two children...
		while (holeInd < limit) {
			// ... move up its smaller child

			size_type childInd = 2 * holeInd + 1; // left child
			if (!compare(container[childInd], container[childInd + 1])) {
				// right child <= left child
				childInd++; // set childInd to index of right child
			}

			container[holeInd] = std::move(container[childInd]);
			setIndex(container[holeInd], holeInd);
			holeInd = childInd;
		}

		// if the container has a lone left child and the hole is at this child's parent index...
		if ((len & 1) == 0 && holeInd == (len - 2) / 2) {
			// ... move up the lone left child
			container[holeInd] = std::move(container[len - 1]);
			setIndex(container[holeInd], holeInd);
			holeInd = len - 1;
		}

		siftUp(holeInd, startInd, std::move(value));
	}

	void buildHeap() {
		if (container.size() < 2)
			return;

		// starts at the index i with at least one child; iPlusOne = i + 1
		for (size_type iPlusOne = (container.size() - 2) / 2 + 1; iPlusOne > 0; --iPlusOne) {
			const size_type i = iPlusOne - 1;
			value_type value = std::move(container[i]);
			siftDown(i, std::move(value));
		}

	}

	void fixPushed() {
		value_type val = std::move(container.back());
		siftUp(container.size() - 1, 0, std::move(val));
	}

	void fixValue(size_type ind, value_type&& value) {
		if ((
				2 * ind + 1 < container.size() && compare(container[2 * ind + 1], value) // left child < value?
			) || (
				2 * ind + 2 < container.size() && compare(container[2 * ind + 2], value) // right child < value?
		))
			siftDown(ind, std::move(value));
		else
			siftUp(ind, 0, std::move(value));
	}

	bool verify() const {
		for (auto i = container.begin(); i != container.end(); ++i) {
			const auto ind = i - container.begin();

			const auto leftChildInd = 2 * ind + 1;
			const auto rightChildInd = leftChildInd + 1;
			if (leftChildInd < container.size() and compare(container[leftChildInd], *i))
					return false;
			if (rightChildInd < container.size() and compare(container[rightChildInd], *i))
					return false;
		}
		return true;
	}
public:
	BinHeap() : BinHeap(Compare(), SetIndex(), Container()) {}
	BinHeap(const Compare& comp, const SetIndex& setInd, const Container& cont) : container(cont), compare(comp), setIndex(setInd) {
		buildHeap();
	}
	BinHeap(const Compare& comp, const SetIndex& setInd, Container&& cont) : container(cont), compare(comp), setIndex(setInd) {
		buildHeap();
	}
	template<class InputIt>
	BinHeap(InputIt first, InputIt last, const Compare& comp, const SetIndex& setInd, const Container& cont) : container(cont), compare(comp), setIndex(setInd) {
		container.insert(container.end(), first, last);
		buildHeap();
	}
	template<class InputIt>
	BinHeap(InputIt first, InputIt last, const Compare& comp = Compare(), const SetIndex& setInd = SetIndex(), Container&& cont = Container()) : container(cont), compare(comp), setIndex(setInd) {
		container.insert(container.end(), first, last);
		buildHeap();
	}

	void push(const value_type& value) {
		container.push_back(value);
		fixPushed();
	}
	void push(value_type&& value) {
		container.push_back(std::move(value));
		fixPushed();
	}

	template<class... Args>
	void emplace(Args&&... args) {
		container.emplace_back(std::forward<Args>(args)...);
		fixPushed();
	}

	void fix(size_type ind) {
		value_type value = std::move(container[ind]);
		fixValue(ind, std::move(value));
	}
	void fix(iterator it) {
		fix(it - begin());
	}
	void fix(const_iterator it) {
		fix(it - cbegin());
	}

	void remove(size_type ind) {
		value_type value = std::move(container.back());
		container.pop_back();
		fixValue(ind, std::move(value));
	}
	void remove(iterator it) {
		remove(it - begin());
	}
	void remove(const_iterator it) {
		remove(it - cbegin());
	}

	void pop() {
		value_type value = std::move(container.back());
		siftDown(0, std::move(value));
		container.pop_back();
	}

	bool empty() const {
		return container.empty();
	}
	size_type size() const {
		return container.size();
	}

	reference top() {
		return container.front();
	}

	const_reference top() const {
		return container.front();
	}

	iterator begin() {
		return container.begin();
	}
	iterator end() {
		return container.end();
	}

	const_iterator begin() const {
		return container.begin();
	}
	const_iterator end() const {
		return container.end();
	}

	const_iterator cbegin() const {
		return container.cbegin();
	}
	const_iterator cend() const {
		return container.cend();
	}
};

template<class T>
class MinHeapCompare {
public:
	bool operator()(const T& lhs, const T& rhs) const {
		return lhs.minHeapCompare(rhs);
	}
};

template<class T>
class MaxHeapCompare {
public:
	bool operator()(const T& lhs, const T& rhs) const {
		return lhs.maxHeapCompare(rhs);
	}
};

template<
	class T,
	class Container = std::vector<T>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
using MinBinHeap = BinHeap<T, Container, MinHeapCompare<T>, SetIndex>;

template<
	class T,
	class Container = std::vector<T>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
using MaxBinHeap = BinHeap<T, Container, MaxHeapCompare<T>, SetIndex>;

#endif